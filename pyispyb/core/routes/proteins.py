import logging

from fastapi import Depends, HTTPException, status
from ispyb import models

from ...dependencies import order_by_factory, pagination
from ...app.extensions.database.utils import Paged
from ... import filters
from ...app.base import AuthenticatedAPIRouter

from ..modules import proteins as crud
from ..schemas import protein as schema
from ..schemas.utils import paginated, make_optional


logger = logging.getLogger(__name__)
router = AuthenticatedAPIRouter(prefix="/proteins", tags=["Proteins"])


@router.get("", response_model=paginated(schema.Protein))
def get_proteins(
    page: dict[str, int] = Depends(pagination),
    proteinId: int = Depends(filters.proteinId),
    proposal: str = Depends(filters.proposal),
    search: str = Depends(filters.search),
    sort_order: dict = Depends(order_by_factory(crud.ORDER_BY_MAP, "ProteinOrder")),
) -> Paged[models.BLSample]:
    """Get a list of proteins"""
    logging.info(f"get_proteins for proposal {proposal}")
    return crud.get_proteins(
        proteinId=proteinId,
        proposal=proposal,
        search=search,
        sort_order=sort_order,
        **page,
    )


@router.get(
    "/{proteinId}",
    response_model=schema.Protein,
    responses={404: {"description": "No such protein"}},
)
def get_protein(
    proteinId: int = Depends(filters.proteinId),
) -> models.Protein:
    """Get a protein"""
    proteins = crud.get_proteins(
        proteinId=proteinId,
        skip=0,
        limit=1,
    )

    try:
        return proteins.first
    except IndexError:
        raise HTTPException(status_code=404, detail="Protein not found")


@router.post(
    "",
    response_model=schema.Protein,
    status_code=status.HTTP_201_CREATED,
)
def create_protein(protein: schema.ProteinCreate) -> models.Protein:
    """Create a new protein"""
    return crud.create_protein(
        protein=protein,
    )


PROTEIN_UPDATE_EXCLUDED = {}


@router.patch(
    "/{proteinId}",
    response_model=schema.Protein,
    responses={
        404: {"description": "No such protein"},
        400: {"description": "Could not update protein"},
    },
)
def update_protein(
    proteinId: int,
    protein: make_optional(
        schema.Protein,
        exclude=PROTEIN_UPDATE_EXCLUDED,
    ),
):
    """Update a Protein"""
    try:
        return crud.update_protein(proteinId, protein)
    except IndexError:
        raise HTTPException(status_code=404, detail="Protein not found")
    except Exception:
        logger.exception(
            f"Could not update protein `{proteinId}` with payload `{protein}`"
        )
        raise HTTPException(status_code=400, detail="Could not update protein")
