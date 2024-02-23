from typing import Optional
from datetime import datetime

from sqlalchemy import or_, func, distinct
from sqlalchemy.orm import contains_eager
from ispyb import models

from ...app.extensions.database.utils import (
    Paged,
    page,
    update_model,
    with_metadata,
    order,
)

from ...app.extensions.database.middleware import db
from ...app.extensions.database.definitions import with_authorization
from ...core.modules.utils import encode_external_id
from ..schemas import protein as schema


ORDER_BY_MAP = {
    "proteinId": models.Protein.proteinId,
    "acronym": models.Protein.acronym,
    "name": models.Protein.name,
}


def create_protein(protein: schema.ProteinCreate) -> models.Protein:
    protein_dict = protein.dict()
    protein_dict["name"] = protein.name
    protein_dict["acronym"] = protein.acronym
    protein_dict["bltimeStamp"] = datetime.now()

    protein = models.Protein(**protein_dict)
    db.session.add(protein)
    db.session.commit()

    new_protein = get_proteins(proteinId=protein.proteinId, skip=0, limit=1)
    return new_protein.first


def get_proteins(
    skip: int,
    limit: int,
    proteinId: Optional[int] = None,
    proposalId: Optional[int] = None,
    proposal: Optional[str] = None,
    externalId: Optional[int] = None,
    name: Optional[str] = None,
    acronym: Optional[str] = None,
    search: Optional[str] = None,
    sort_order: Optional[dict[str, str]] = None,
    withAuthorization: bool = True,
) -> Paged[models.Protein]:
    metadata = {
        "pdbs": func.count(distinct(models.ProteinHasPDB.proteinid)),
        "samples": func.count(distinct(models.BLSample.blSampleId)),
        "crystals": func.count(distinct(models.Crystal.crystalId)),
    }

    query = (
        db.session.query(models.Protein, *metadata.values())
        .join(models.Proposal)
        # .outerjoin(
        #     models.ConcentrationType,
        #     models.ConcentrationType.concentrationTypeId
        #     == models.Protein.concentrationTypeId,
        # )
        # .options(contains_eager(models.Protein.ConcentrationType))
        .outerjoin(models.ComponentType)
        .options(contains_eager(models.Protein.ComponentType))
        .outerjoin(models.ProteinHasPDB)
        .outerjoin(models.Crystal)
        .outerjoin(models.BLSample)
        .group_by(models.Protein.proteinId)
    )

    if withAuthorization:
        query = with_authorization(query)

    if proteinId:
        query = query.filter(models.Protein.proteinId == proteinId)

    if name:
        query = query.filter(models.Protein.name == name)

    if acronym:
        query = query.filter(models.Protein.acronym == acronym)

    if proposalId:
        query = query.filter(models.Protein.proposalId == proposalId)

    if proposal:
        query = query.filter(models.Proposal.proposal == proposal)

    if externalId:
        externalId = encode_external_id(externalId)
        query = query.filter(models.Protein.externalId == externalId)

    if search:
        query = query.filter(
            or_(
                models.Protein.name.like(f"%{search}%"),
                models.Protein.acronym.like(f"%{search}%"),
            )
        )

    if sort_order:
        query = order(query, ORDER_BY_MAP, sort_order)

    total = query.count()
    query = page(query, skip=skip, limit=limit)

    results = with_metadata(query.all(), list(metadata.keys()))

    protein_ids = [result.proteinId for result in results]
    dc_query = (
        db.session.query(
            models.Protein.proteinId,
            func.count(distinct(models.DataCollection.dataCollectionId)).label(
                "datacollections"
            ),
        )
        .join(models.Crystal)
        .join(models.BLSample)
        .join(
            models.DataCollectionGroup,
            models.BLSample.blSampleId == models.DataCollectionGroup.blSampleId,
        )
        .join(models.DataCollection)
        .filter(models.Protein.proteinId.in_(protein_ids))
        .group_by(models.Protein.proteinId)
    )

    dc_counts = {}
    for dc in dc_query.all():
        row = dc._asdict()
        dc_counts[row["proteinId"]] = row["datacollections"]

    for result in results:
        result._metadata["datacollections"] = dc_counts.get(result.proteinId, 0)

    return Paged(total=total, results=results, skip=skip, limit=limit)


def update_protein(proteinId: int, protein: schema.Protein) -> models.Protein:
    protein_dict = protein.dict(exclude_unset=True)
    new_protein = get_proteins(proteinId=proteinId, skip=0, limit=1).first

    update_model(new_protein, protein_dict)
    db.session.commit()

    return get_proteins(proteinId=proteinId, skip=0, limit=1).first
