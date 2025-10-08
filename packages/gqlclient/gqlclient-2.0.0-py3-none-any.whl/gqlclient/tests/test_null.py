"""
Tests for NULL processing
"""

from typing import Any

import pytest
from pydantic import BaseModel
from pydantic import ValidationError

from gqlclient.base import GraphQLClientBase
from gqlclient.null import NULL
from gqlclient.null import NullType


class Basemodel(BaseModel):
    value: str = "basemodel"
    optInt: int | None = None
    nullableInt: int | NullType = NULL


@pytest.mark.parametrize(
    "request_params",
    [
        pytest.param(Basemodel(), id="basemodel"),
    ],
)
def test_null(request_params: BaseModel):
    """
    Verify None fields are excluded from the resulting string.
    Verify NULL field gets retained with a value of `null`.
    """
    result_string = GraphQLClientBase._graphql_query_parameters_from_model(model=request_params)
    assert "value" in result_string
    assert "optInt" not in result_string
    assert "nullableInt" in result_string
    for kv_string in result_string.split(","):
        k, v = kv_string.split(":")
        if k.strip() == "nullableInt":
            assert v.strip() == "null"


@pytest.mark.parametrize(
    "request_param",
    [
        pytest.param({"optInt": "a_string"}, id="opt_with_str"),
        pytest.param({"nullableInt": "a_string"}, id="null_with_str"),
        pytest.param({"optInt": NULL}, id="opt_with_null"),
        pytest.param({"nullableInt": None}, id="null_with_none"),
    ],
)
def test_null_invalid_basemodel(request_param: dict[str, Any]):
    """
    Verify ValidationError for invalid inputs to BaseModel.
    """
    with pytest.raises(ValidationError):
        Basemodel(**request_param)
