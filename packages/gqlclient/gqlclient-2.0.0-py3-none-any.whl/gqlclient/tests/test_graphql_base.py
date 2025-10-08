"""
Tests for the graphql_client library
"""

from datetime import datetime
from typing import Any

import pytest
from pydantic import BaseModel

from gqlclient import GraphQLClient
from gqlclient.base import dynamic_mutation_param_wrapper
from gqlclient.base import dynamic_query_param_wrapper
from gqlclient.exceptions import ModelException
from gqlclient.request_wrap import AbstractWrap
from gqlclient.request_wrap import DynamicWrap
from gqlclient.request_wrap import StaticWrap

QUERY_BASE = "query_base"
MUTATION_BASE = "mutation_base"


class BasemodelRequest(BaseModel):
    str_param: str
    int_param: int
    float_param: float
    str_array_param: list[str]
    num_array_param: list[int]
    bool_param: bool
    date_param: datetime
    optional_param: int | None = None


class OptBasemodelRequest(BaseModel):
    str_param: str | None = None
    int_param: int | None = None
    float_param: float | None = None
    str_array_param: list[str] | None = None
    num_array_param: list[int] | None = None
    bool_param: bool | None = None
    date_param: datetime | None = None


class StaticNestedBasemodelRequest(StaticWrap):
    request_params: BasemodelRequest
    param_name: str = "testParams"


class DynamicNestedBasemodelRequest(DynamicWrap):
    request_params: BasemodelRequest


class BasemodelResponseChild(BaseModel):
    child_param_1: str
    child_param_2: str


class BasemodelResponseParent(BaseModel):
    parent_param_1: str
    parent_param_2: str
    child_object: BasemodelResponseChild


class BasemodelResponseParentWithList(BaseModel):
    parent_param_1: str
    parent_param_2: str
    child_object: list[BasemodelResponseChild]


basemodel_request = BasemodelRequest(
    str_param="A",
    int_param=1,
    float_param=1.1,
    str_array_param=["A", "B"],
    num_array_param=[1, 2],
    bool_param=False,
    date_param=datetime.strptime("2010-03-25T14:08:00", "%Y-%m-%dT%H:%M:%S"),
)

# static param_name from basemodel definition
static_nested_basemodel_request = StaticNestedBasemodelRequest(
    request_params=basemodel_request,
)

dynamic_nested_basemodel_request = DynamicNestedBasemodelRequest(
    request_params=basemodel_request,
)


class BadModel:
    def __init__(self):
        self.str_param = ("A",)
        self.int_param = (1,)
        self.float_param = (1.1,)
        self.str_array_param = (["A", "B"],)
        self.num_array_param = ([1, 2],)
        self.date_param = datetime.strptime("2010-03-25T14:08:00", "%Y-%m-%dT%H:%M:%S")


bad_model = BadModel()


# Graphql Client to test
@pytest.fixture(scope="module")
def client() -> GraphQLClient:
    return GraphQLClient(gql_uri="http://localhost:5000/graphql")


@pytest.mark.parametrize(
    "query_base, request_params, response_cls",
    [
        pytest.param(
            QUERY_BASE, basemodel_request, BasemodelResponseParent, id="basemodel_instance"
        ),
        pytest.param(
            QUERY_BASE,
            basemodel_request,
            BasemodelResponseParentWithList,
            id="basemodel_instance_with_list",
        ),
    ],
)
def test_query_passthrough_with_parameters(
    query_base: str,
    request_params: BaseModel,
    response_cls: type[BaseModel],
    client,
):
    """
    Test of query string structure when request params are included for passthrough
    :param client: Graphql Client instance
    :param query_base: Name of the query endpoint
    :param request_params: Instance of a BaseModel containing the request parameters
    :param response_cls: BaseModel specifying the attributes of the graphql response
    """
    assert not isinstance(
        request_params, AbstractWrap
    ), "Invalid test fixture. Cannot be AbstractWrap for this test."

    test_query = client.get_query(
        query_base=query_base, query_parameters=request_params, query_response_cls=response_cls
    )
    assert "query" in test_query
    expected_query_str = (
        "{query_base("
        'str_param: "A", '
        "int_param: 1, "
        "float_param: 1.1, "
        'str_array_param: ["A", "B"], '
        "num_array_param: [1, 2], "
        "bool_param: false, "
        'date_param: "2010-03-25T14:08:00")'
        "{parent_param_1, parent_param_2, "
        "child_object { child_param_1 child_param_2 }"
        "} }"
    )
    assert test_query["query"] == expected_query_str


@pytest.mark.parametrize(
    "query_base, request_object, response_cls",
    [
        pytest.param(
            QUERY_BASE,
            static_nested_basemodel_request,
            BasemodelResponseParent,
            id="basemodel_static_request",
        ),
        pytest.param(
            QUERY_BASE,
            static_nested_basemodel_request,
            BasemodelResponseParentWithList,
            id="basemodel_static_request_with_list",
        ),
    ],
)
def test_query_static_nest_with_parameters(
    query_base: str,
    request_object: BaseModel,
    response_cls: type[BaseModel],
    client,
):
    """
    Test of query string structure when request params and `param_name` are included
    :param client: Graphql Client instance
    :param query_base: Name of the query endpoint
    :param request_object: Instance of a StaticWrap BaseModel containing the `request_params` and static `param_name`
    :param response_cls: BaseModel specifying the attributes of the graphql response
    """
    assert isinstance(
        request_object, StaticWrap
    ), "Invalid test fixture. StaticWrap required for this test."

    test_query = client.get_query(
        query_base=query_base, query_parameters=request_object, query_response_cls=response_cls
    )
    param_wrapper = request_object.param_name
    assert "query" in test_query
    expected_query_str = (
        "{query_base("
        f"{param_wrapper}: "
        '{str_param: "A", '
        "int_param: 1, "
        "float_param: 1.1, "
        'str_array_param: ["A", "B"], '
        "num_array_param: [1, 2], "
        "bool_param: false, "
        'date_param: "2010-03-25T14:08:00"})'
        "{parent_param_1, parent_param_2, "
        "child_object { child_param_1 child_param_2 }"
        "} }"
    )
    assert test_query["query"] == expected_query_str


@pytest.mark.parametrize(
    "query_base, request_object, response_cls",
    [
        pytest.param(
            QUERY_BASE,
            dynamic_nested_basemodel_request,
            BasemodelResponseParent,
            id="basemodel_request",
        ),
        pytest.param(
            QUERY_BASE,
            dynamic_nested_basemodel_request,
            BasemodelResponseParentWithList,
            id="basemodel_request_with_list",
        ),
    ],
)
def test_query_dynamic_nest_with_parameters(
    query_base: str,
    request_object: BaseModel,
    response_cls: type[BaseModel],
    client,
):
    """
    Test of query string structure when request params are included and `param_name` will be determined dynamically
    :param client: Graphql Client instance
    :param query_base: Name of the query endpoint
    :param request_object: Instance of a DynamicWrap containing the `request_params`
    :param response_cls: BaseModel specifying the attributes of the graphql response
    """
    assert isinstance(
        request_object, DynamicWrap
    ), "Invalid test fixture. DynamicWrap required for this test."

    test_query = client.get_query(
        query_base=query_base, query_parameters=request_object, query_response_cls=response_cls
    )
    param_wrapper = dynamic_query_param_wrapper()
    assert "query" in test_query
    expected_query_str = (
        "{query_base("
        f"{param_wrapper}: "
        '{str_param: "A", '
        "int_param: 1, "
        "float_param: 1.1, "
        'str_array_param: ["A", "B"], '
        "num_array_param: [1, 2], "
        "bool_param: false, "
        'date_param: "2010-03-25T14:08:00"})'
        "{parent_param_1, parent_param_2, "
        "child_object { child_param_1 child_param_2 }"
        "} }"
    )
    assert test_query["query"] == expected_query_str


@pytest.mark.parametrize(
    "query_base, response_cls",
    [
        pytest.param(QUERY_BASE, BasemodelResponseParent, id="basemodel_response"),
        pytest.param(
            QUERY_BASE, BasemodelResponseParentWithList, id="basemodel_response_with_list"
        ),
    ],
)
def test_query_without_parameters(client, query_base: str, response_cls: type[BaseModel]):
    """
    Test of query string structure when parameter model is NOT included
    :param client: Graphql Client instance
    :param query_base: Name of the query endpoint
    :param response_cls: BaseModel specifying the attributes of the graphql response
    """
    test_query = client.get_query(query_base=query_base, query_response_cls=response_cls)
    assert "query" in test_query
    expected_query_str = (
        "{query_base"
        "{parent_param_1, parent_param_2, "
        "child_object { child_param_1 child_param_2 }"
        "} }"
    )

    assert test_query["query"] == expected_query_str


@pytest.mark.parametrize(
    "mutation_base, request_params, response_cls",
    [
        pytest.param(MUTATION_BASE, basemodel_request, BasemodelResponseParent, id="basemodel"),
        pytest.param(
            MUTATION_BASE,
            basemodel_request,
            BasemodelResponseParentWithList,
            id="basemodel_with_list",
        ),
    ],
)
def test_mutation_passthrough_with_response(
    client, mutation_base: str, request_params: BaseModel, response_cls: type[BaseModel]
):
    """
    Test of mutation string structure when response model is included and request params are included for passthrough
    :param client: Graphql Client instance
    :param mutation_base: Name of the mutation endpoint
    :param request_params: Instance of a BaseModel containing the request parameters
    :param response_cls: BaseModel specifying the attributes of the graphql response
    """
    assert not isinstance(
        request_params, AbstractWrap
    ), "Invalid test fixture. Cannot be AbstractWrap for this test."

    test_mutation = client.get_mutation(
        mutation_base=mutation_base,
        mutation_response_cls=response_cls,
        mutation_parameters=request_params,
    )
    assert "query" in test_mutation
    assert "operationName" in test_mutation
    expected_query_str = (
        "mutation mutation_base "
        "{mutation_base("
        'str_param: "A", '
        "int_param: 1, "
        "float_param: 1.1, "
        'str_array_param: ["A", "B"], '
        "num_array_param: [1, 2], "
        "bool_param: false, "
        'date_param: "2010-03-25T14:08:00")'
        "{parent_param_1, parent_param_2, child_object "
        "{ child_param_1 child_param_2 }} }"
    )

    assert test_mutation["query"] == expected_query_str
    assert test_mutation["operationName"] == "mutation_base"


@pytest.mark.parametrize(
    "mutation_base, request_object, response_cls",
    [
        pytest.param(
            MUTATION_BASE,
            static_nested_basemodel_request,
            BasemodelResponseParent,
            id="basemodel_static_request",
        ),
        pytest.param(
            MUTATION_BASE,
            static_nested_basemodel_request,
            BasemodelResponseParentWithList,
            id="basemodel_static_request_with_list",
        ),
    ],
)
def test_mutation_static_nest_with_response(
    client, mutation_base: str, request_object: BaseModel, response_cls: type[BaseModel]
):
    """
    Test of mutation string structure when response model is included and request params and `param_name` are included
    :param client: Graphql Client instance
    :param mutation_base: Name of the mutation endpoint
    :param request_object: Instance of a StaticWrap BaseModel containing the `request_params` and static `param_name`
    :param response_cls: BaseModel containing the attributes of the graphql response
    """
    assert isinstance(
        request_object, StaticWrap
    ), "Invalid test fixture. StaticWrap required for this test."

    test_mutation = client.get_mutation(
        mutation_base=mutation_base,
        mutation_response_cls=response_cls,
        mutation_parameters=request_object,
    )
    param_wrapper = request_object.param_name
    assert "query" in test_mutation
    assert "operationName" in test_mutation
    expected_query_str = (
        "mutation mutation_base "
        "{mutation_base("
        f"{param_wrapper}: "
        '{str_param: "A", '
        "int_param: 1, "
        "float_param: 1.1, "
        'str_array_param: ["A", "B"], '
        "num_array_param: [1, 2], "
        "bool_param: false, "
        'date_param: "2010-03-25T14:08:00"})'
        "{parent_param_1, parent_param_2, child_object "
        "{ child_param_1 child_param_2 }} }"
    )

    assert test_mutation["query"] == expected_query_str
    assert test_mutation["operationName"] == "mutation_base"


@pytest.mark.parametrize(
    "mutation_base, request_object, response_cls",
    [
        pytest.param(
            MUTATION_BASE,
            dynamic_nested_basemodel_request,
            BasemodelResponseParent,
            id="basemodel_dynamic_request",
        ),
        pytest.param(
            MUTATION_BASE,
            dynamic_nested_basemodel_request,
            BasemodelResponseParentWithList,
            id="basemodel_dynamic_request_with_list",
        ),
    ],
)
def test_mutation_dynamic_nest_with_response(
    mutation_base: str,
    request_object: BaseModel,
    response_cls: type[BaseModel],
    client,
):
    """
    Test of mutation string structure when response model is included and request params are included
    and `param_name` will be determined dynamically.
    :param client: Graphql Client instance
    :param mutation_base: Name of the mutation endpoint
    :param request_object: Instance of a DynamicWrap BaseModel containing the `request_params`
    :param response_cls: BaseModel specifying the attributes of the graphql response
    """
    assert isinstance(
        request_object, DynamicWrap
    ), "Invalid test fixture. DynamicWrap required for this test."

    test_mutation = client.get_mutation(
        mutation_base=mutation_base,
        mutation_response_cls=response_cls,
        mutation_parameters=request_object,
    )
    param_wrapper = dynamic_mutation_param_wrapper(mutation_base)
    assert "query" in test_mutation
    assert "operationName" in test_mutation
    expected_query_str = (
        "mutation mutation_base "
        "{mutation_base("
        f"{param_wrapper}: "
        '{str_param: "A", '
        "int_param: 1, "
        "float_param: 1.1, "
        'str_array_param: ["A", "B"], '
        "num_array_param: [1, 2], "
        "bool_param: false, "
        'date_param: "2010-03-25T14:08:00"})'
        "{parent_param_1, parent_param_2, child_object "
        "{ child_param_1 child_param_2 }} }"
    )

    assert test_mutation["query"] == expected_query_str
    assert test_mutation["operationName"] == "mutation_base"


@pytest.mark.parametrize(
    "response_model_cls, parameter_model",
    [
        pytest.param(BadModel, None, id="no_params"),
        pytest.param(BasemodelResponseChild, bad_model, id="with_params"),
    ],
)
def test_bad_model(client, response_model_cls: type[BaseModel], parameter_model: Any):
    """
    Test that non-BaseModel objects cause a ValueError
    :param client: Graphql Client instance
    :param response_model_cls: Object representing the graphql response
    :param parameter_model: Object representing the graphql parameters
    """

    with pytest.raises(ModelException):
        client.get_query(QUERY_BASE, response_model_cls, parameter_model)


def test_query_with_empty_parameters(client):
    """
    Test query with a parameter object with all None attribute values
    :param client: Graphql Client instance
    """

    # noinspection PyTypeChecker
    empty_parameters = OptBasemodelRequest()

    test_query = client.get_query(
        query_base=QUERY_BASE,
        query_parameters=empty_parameters,
        query_response_cls=BasemodelResponseParent,
    )
    assert "query" in test_query
    expected_query_str = (
        "{query_base"
        "{parent_param_1, parent_param_2, "
        "child_object { child_param_1 child_param_2 }"
        "} }"
    )

    assert test_query["query"] == expected_query_str


def test_basemodel_three_layered_response(client):
    """
    Test query with a three layer hierarchy
    :param client: Graphql Client instance
    """

    class Grandchild(BaseModel):
        grandchild_name: str

    class Child(BaseModel):
        child_name: str
        grandchild: Grandchild

    class Parent(BaseModel):
        parent_name: str
        child: Child

    test_query = client.get_query("basemodelThreeLayer", Parent)

    expected_query = {
        "query": "{basemodelThreeLayer"
        "{parent_name, "
        "child { child_name grandchild { grandchild_name } }"
        "} }"
    }
    assert test_query == expected_query


def test_encode_by_type(client):
    """
    Test encoding of a `dict` to a string representation of a GQL `ObjectValueNode`
    :param client: Graphql Client instance
    """
    to_encode = {
        "key_str": "string",
        "key_int": 42,
        "key_float": 3.141592,
        "key_none": None,
        "key_true": True,
        "key_false": False,
    }

    actual_output = client._encode_by_type(to_encode)

    expected_output = '{key_str: "string", key_int: 42, key_float: 3.141592, '
    expected_output += "key_none: null, key_true: true, key_false: false}"

    assert actual_output == expected_output
