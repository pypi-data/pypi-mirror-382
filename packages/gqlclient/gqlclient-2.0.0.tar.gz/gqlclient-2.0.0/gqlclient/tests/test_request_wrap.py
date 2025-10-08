"""
Tests for request wrapping
"""

import pytest
from pydantic import BaseModel

from gqlclient.request_wrap import AbstractWrap
from gqlclient.request_wrap import DynamicWrap
from gqlclient.request_wrap import StaticWrap
from gqlclient.request_wrap import wrap_request


class Basemodel(BaseModel):
    value: str = "basemodel"
    optInt: int | None = None


@pytest.mark.parametrize(
    "request_params",
    [
        pytest.param(None, id="none"),
        pytest.param(Basemodel(), id="basemodel"),
    ],
)
def test_dynamic_wrap(request_params: BaseModel | None):
    """Verify proper DynamicWrap instantiation"""
    result: DynamicWrap = DynamicWrap(request_params=request_params)
    assert result
    assert isinstance(result, DynamicWrap)
    result_data = result.model_dump()
    # verify param_name is excluded from result
    assert "param_name" not in result_data.keys()
    assert "request_params" in result_data.keys()
    if request_params is None:
        assert result.request_params is None
    else:
        assert result.request_params == request_params
        assert result.request_params is request_params


@pytest.mark.parametrize(
    "request_params",
    [
        pytest.param(None, id="none"),
        pytest.param(Basemodel(), id="basemodel"),
    ],
)
def test_static_wrap(request_params: BaseModel | None):
    """Verify proper StaticWrap instantiation"""
    result: StaticWrap = StaticWrap(request_params=request_params, param_name="whatever")
    assert result
    assert isinstance(result, StaticWrap)
    result_data = result.model_dump()
    # verify param_name is included in result
    assert "param_name" in result_data.keys()
    assert result_data["param_name"] == "whatever"
    assert "request_params" in result_data.keys()
    if request_params is None:
        assert result.request_params is None
    else:
        assert result.request_params == request_params
        assert result.request_params is request_params


@pytest.mark.parametrize(
    "request_params, expected_exception_type",
    [
        pytest.param(Basemodel(), TypeError, id="basemodel"),
    ],
)
def test_abstract_wrap(request_params, expected_exception_type: type[Exception]):
    """Verify AbstractWrap cannot be instantiated"""
    with pytest.raises(expected_exception_type):
        AbstractWrap(request_params=request_params)


@pytest.mark.parametrize(
    "request_params, expected_exception_type",
    [
        pytest.param("a_string", TypeError, id="string"),
        pytest.param(int, TypeError, id="int"),
        pytest.param({"a_key": "a_value"}, TypeError, id="dict"),
        pytest.param([], TypeError, id="list"),
    ],
)
def test_invalid_wrap(request_params, expected_exception_type: type[Exception]):
    """Verify request params must be a BaseModel"""
    with pytest.raises(expected_exception_type):
        DynamicWrap(request_params=request_params)
    with pytest.raises(expected_exception_type):
        StaticWrap(request_params=request_params, param_name="whatever")


@pytest.mark.parametrize(
    "request_params",
    [
        pytest.param(None, id="none"),
        pytest.param(Basemodel(), id="basemodel_instance"),
    ],
)
def test_wrap_request(request_params: BaseModel | None):
    """Verify proper result from wrap_request"""
    result: DynamicWrap = wrap_request(request_params=request_params)
    assert result
    assert isinstance(result, DynamicWrap)
    result_data = result.model_dump()
    # verify param_name is excluded from result
    assert "param_name" not in result_data.keys()
    assert "request_params" in result_data.keys()
    if request_params is None:
        assert result.request_params is None
    else:
        assert result.request_params == request_params
        assert result.request_params is request_params

    result: StaticWrap = wrap_request(request_params=request_params, param_name="whatever")
    assert result
    assert isinstance(result, StaticWrap)
    result_data = result.model_dump()
    # verify param_name is included in result
    assert "param_name" in result_data.keys()
    assert result_data["param_name"] == "whatever"
    assert "request_params" in result_data.keys()
    if request_params is None:
        assert result.request_params is None
    else:
        assert result.request_params == request_params
        assert result.request_params is request_params


@pytest.mark.parametrize(
    "request_params, expected_exception_type",
    [
        pytest.param(Basemodel, TypeError, id="basemodel_definition"),
    ],
)
def test_wrap_request_invalid_inputs(
    request_params: BaseModel, expected_exception_type: type[Exception]
):
    """Verify proper result from wrap_request for invalid input"""
    with pytest.raises(expected_exception_type):
        wrap_request(request_params=request_params)
    with pytest.raises(expected_exception_type):
        wrap_request(request_params=request_params, param_name="whatever")
