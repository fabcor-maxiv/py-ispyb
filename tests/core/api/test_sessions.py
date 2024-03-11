import pytest

from ispyb import models
from pyispyb.app.extensions.auth import token
from sqlalchemy.orm import Session
from starlette.types import ASGIApp

from tests.conftest import AuthClient
from tests.core.api.data.sessions import (
    test_data_sessions_list,
)
from tests.core.api.utils.apitest import (
    ApiTestElem,
    get_elem_name,
    run_test,
)


@pytest.mark.parametrize("test_elem", test_data_sessions_list, ids=get_elem_name)
def test_session_list(auth_client: AuthClient, test_elem: ApiTestElem, app: ASGIApp):
    run_test(auth_client, test_elem, app)


def test_session_create(auth_client_abcd: AuthClient):
    """Test creating session"""

    payload = {
        "proposalId": 1,
        "startDate": "2000-01-01T00:00:00",
        "endDate": "2099-01-01T23:59:59",
        "beamLineName": "bl",
        "scheduled": True,
        "nbShifts": 0,
        "comments": "This is a comment",
        "BeamLineSetup": {
            "synchrotronMode": "synchrotronMode",
            "minTransmission": 0.0,
        },
    }
    resp = auth_client_abcd.post(
        "/sessions/",
        payload=payload,
    )
    assert 201 == resp.status_code
    data = resp.json()
    assert "sessionId" in data
    assert type(data["sessionId"]) is int
    assert "synchrotronMode" == data["BeamLineSetup"]["synchrotronMode"]


def test_session_create_without_beamline_setup(auth_client_abcd: AuthClient):
    """Test creating session without beamline setup"""

    payload = {
        "proposalId": 1,
        "startDate": "2000-01-01T00:00:00",
        "endDate": "2099-01-01T23:59:59",
        "beamLineName": "bl",
        "scheduled": True,
        "nbShifts": 0,
        "comments": "This is a comment",
    }
    resp = auth_client_abcd.post(
        "/sessions/",
        payload=payload,
    )
    assert 201 == resp.status_code
    data = resp.json()
    assert "BeamLineSetup" in data
    assert isinstance(data["BeamLineSetup"], dict)
    assert "synchrotronMode" in data["BeamLineSetup"]
    assert data["BeamLineSetup"]["synchrotronMode"] is None


def test_session_create_with_empty_beamline_setup(auth_client_abcd: AuthClient):
    """Test creating session with empty beamline setup"""

    payload = {
        "proposalId": 1,
        "startDate": "2000-01-01T00:00:00",
        "endDate": "2099-01-01T23:59:59",
        "beamLineName": "bl",
        "scheduled": True,
        "nbShifts": 0,
        "comments": "This is a comment",
        "BeamLineSetup": {},
    }
    resp = auth_client_abcd.post(
        "/sessions/",
        payload=payload,
    )
    assert 201 == resp.status_code
    data = resp.json()
    assert "BeamLineSetup" in data
    assert isinstance(data["BeamLineSetup"], dict)
    assert "synchrotronMode" in data["BeamLineSetup"]
    assert data["BeamLineSetup"]["synchrotronMode"] is None


@pytest.fixture
def beamline_session(auth_client_abcd: AuthClient, with_db_session: Session):

    token_data = token.decode_token(auth_client_abcd.token)

    # Create a beamline session (via REST API)
    create_payload = {
        "proposalId": 1,
        "startDate": "2000-01-01T00:00:00",
        "endDate": "2099-01-01T23:59:59",
        "beamLineName": "bl",
        "scheduled": True,
        "nbShifts": 0,
        "comments": "This is a comment",
    }
    record_id = auth_client_abcd.post(
        "/sessions/",
        payload=create_payload,
    ).json()["sessionId"]

    # Assign the user to the newly created session (directly via ORM)
    session_has_person = models.SessionHasPerson(
        personId=token_data["personId"],
        sessionId=record_id,
    )
    with_db_session.add(session_has_person)
    with_db_session.commit()

    yield record_id


def test_session_update_nothing(auth_client_abcd: AuthClient, beamline_session: int):
    """Test updating session by updating nothing."""

    # Updating nothing should succeed
    update_payload = {
        "BeamLineSetup": {},
    }
    resp = auth_client_abcd.patch(
        f"/sessions/{beamline_session}",
        payload=update_payload,
    )
    assert 200 == resp.status_code
    data = resp.json()
    assert "BeamLineSetup" in data
    assert isinstance(data["BeamLineSetup"], dict)
    assert "synchrotronMode" in data["BeamLineSetup"]
    assert data["BeamLineSetup"]["synchrotronMode"] is None


def test_session_update_add_beamline_setup(
    auth_client_abcd: AuthClient, beamline_session: int
):
    """Test updating session by adding beamline setup."""

    update_payload = {
        "BeamLineSetup": {
            "synchrotronMode": "synchrotronMode",
            "minTransmission": 0.0,
        },
    }
    resp = auth_client_abcd.patch(
        f"/sessions/{beamline_session}",
        payload=update_payload,
    )
    assert 200 == resp.status_code
    data = resp.json()
    assert data["BeamLineSetup"]["synchrotronMode"] == "synchrotronMode"


def test_session_update_remove_beamline_setup(
    auth_client_abcd: AuthClient, beamline_session: int
):
    """Test updating session by removing beamline setup."""

    # Removing beamline setup is not allowed
    update_payload = {
        "BeamLineSetup": None,
    }
    resp = auth_client_abcd.patch(
        f"/sessions/{beamline_session}",
        payload=update_payload,
    )
    assert 422 == resp.status_code
