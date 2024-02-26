import logging
from fastapi import HTTPException, Depends
from ...modules import userportalsync as crud
from ...schemas import userportalsync as schema
from pyispyb import filters
from ....dependencies import permission
from ..responses import Message
from ....app.base import AuthenticatedAPIRouter

router = AuthenticatedAPIRouter(
    prefix="/webservices/userportalsync",
    tags=["Webservices - User portal sync"],
    dependencies=[Depends(permission("uportal_sync"))],
)

logger = logging.getLogger("ispyb")


@router.post(
    "/sync_proposal",
    response_model=Message,
    responses={400: {"description": "The input data is not following the schema"}},
)
def sync_proposal(
    proposal: schema.UserPortalProposalSync,
):
    """Create/Update a proposal from the User Portal and all its related entities"""
    try:
        logger.info(f"Calling sync_proposal function with proposal:{proposal}")
        execution_time = crud.sync_proposal(proposal=proposal)
        proposal_dict = proposal.dict()
        return {
            "message": f"The proposal {proposal_dict['proposal']['proposalCode']}"
            f"-{proposal_dict['proposal']['proposalNumber']} has been synchronized in {execution_time} seconds"
        }

    except Exception as e:
        logging.exception("sync_proposal failed")
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/sync_proposal/{proposal}/message",
    response_model=Message,
    responses={400: {"description": "The input data is not following the schema"}},
)
def create_sync_message(
    proposal: str = Depends(filters.proposal),
):
    """Create a rabbitmq message to call the synchronization process between the User Portal and ISPyB"""
    try:
        logger.info(f"Calling create_sync_message function for proposal {proposal}")
        execution_time = crud.create_sync_message(proposal=proposal)
        return {
            "message": f"The message for the proposal {proposal} has been created in the RabbitMQ server in {execution_time} seconds"
        }

    except Exception as e:
        logging.exception("create_sync_message failed")
        raise HTTPException(status_code=400, detail=str(e))
