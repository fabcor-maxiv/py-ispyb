import pytest

from starlette.types import ASGIApp

from tests.conftest import AuthClient
from tests.core.api.utils.apitest import get_elem_name, run_test, ApiTestElem

from tests.core.api.data.proteins import (
    test_route_proteins_list,
    test_route_protein_create,
)


@pytest.mark.parametrize("test_elem", test_route_proteins_list, ids=get_elem_name)
def test_proteins_list(auth_client: AuthClient, test_elem: ApiTestElem, app: ASGIApp):
    run_test(auth_client, test_elem, app)


@pytest.mark.parametrize("test_elem", test_route_protein_create, ids=get_elem_name)
def test_protein_create(auth_client: AuthClient, test_elem: ApiTestElem, app: ASGIApp):
    run_test(auth_client, test_elem, app)
