from tests.core.api.utils.apitest import ApiTestElem, ApiTestExpected, ApiTestInput


test_route_proteins_list = [
    ApiTestElem(
        name="List proteins",
        input=ApiTestInput(
            login="abcd",
            route="/proteins",
        ),
        expected=ApiTestExpected(
            code=200,
        ),
    ),
    ApiTestElem(
        name="Get a protein",
        input=ApiTestInput(
            login="abcd",
            route="/proteins/1",
        ),
        expected=ApiTestExpected(
            code=200,
        ),
    ),
    ApiTestElem(
        name="List proteins (admin)",
        input=ApiTestInput(
            permissions=[
                "bl_admin",
            ],
            login="efgh",
            route="/proteins",
        ),
        expected=ApiTestExpected(
            code=200,
        ),
    ),
]

test_data_protein_create = {
    "name": "MyNewProtein",
    "acronym": "myNewProt",
    "proposalId": 1,
}

test_route_protein_create = [
    ApiTestElem(
        name="Create protein",
        input=ApiTestInput(
            login="abcd",
            permissions=["abcd"],
            route="/proteins",
            method="post",
            payload=test_data_protein_create,
        ),
        expected=ApiTestExpected(
            code=201,
        ),
    ),
]
