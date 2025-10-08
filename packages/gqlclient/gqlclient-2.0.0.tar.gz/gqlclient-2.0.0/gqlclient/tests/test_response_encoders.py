"""
Tests for the response_encoders library
"""

from typing import Any
from typing import Callable

import pytest
from pydantic import BaseModel

from gqlclient import basemodel_encoder
from gqlclient import dataclass_encoder
from gqlclient import dict_encoder
from gqlclient import json_encoder
from gqlclient.exceptions import EncoderResponseException


class BasemodelChildResponseModel(BaseModel):
    s: str
    i: int


class BasemodelParentResponseModel(BaseModel):
    a: str
    c: BasemodelChildResponseModel


@pytest.mark.parametrize(
    "call_base, response, response_cls, expected_response_cls_instance",
    [
        (  # basemodel query response without a list
            "call",
            {"call": {"a": "foo", "c": {"s": "bar", "i": 1}}},
            BasemodelParentResponseModel,
            BasemodelParentResponseModel(a="foo", c=BasemodelChildResponseModel(s="bar", i=1)),
        ),
        (  # basemodel query response with a list
            "call",
            {
                "call": [
                    {"a": "foo1", "c": {"s": "bar1", "i": 1}},
                    {"a": "foo2", "c": {"s": "bar2", "i": 2}},
                ]
            },
            BasemodelParentResponseModel,
            [
                BasemodelParentResponseModel(
                    a="foo1", c=BasemodelChildResponseModel(s="bar1", i=1)
                ),
                BasemodelParentResponseModel(
                    a="foo2", c=BasemodelChildResponseModel(s="bar2", i=2)
                ),
            ],
        ),
    ],
)
def test_basemodel_encoder(
    call_base: str,
    response: dict,
    response_cls: type[BaseModel],
    expected_response_cls_instance: BaseModel | list[BaseModel],
):
    assert basemodel_encoder(call_base, response, response_cls) == expected_response_cls_instance


@pytest.mark.parametrize(
    "call_base, response, response_cls, expected_response_cls_instance",
    [
        (  # response without a list
            "foo",
            {"call": {"a": "foo", "c": {"s": "bar", "i": 1}}},
            BasemodelParentResponseModel,
            '{"call": {"a": "foo", "c": {"s": "bar", "i": 1}}}',
        ),
        (  # response with a list
            "foo",
            {
                "call": [
                    {"a": "foo1", "c": {"s": "bar1", "i": 1}},
                    {"a": "foo2", "c": {"s": "bar2", "i": 2}},
                ]
            },
            BasemodelParentResponseModel,
            '{"call": [{"a": "foo1", "c": {"s": "bar1", "i": 1}}, {"a": "foo2", "c": {"s": "bar2", "i": 2}}]}',
        ),
    ],
)
def test_json_encoder(
    call_base: str,
    response: dict,
    response_cls: type[BaseModel],
    expected_response_cls_instance: str,
) -> None:
    assert json_encoder(call_base, response, response_cls) == expected_response_cls_instance


@pytest.mark.parametrize(
    "call_base, response, response_cls, expected_response_cls_instance",
    [
        (  # response without a list
            "foo",
            {"call": {"a": "foo", "c": {"s": "bar", "i": 1}}},
            BasemodelParentResponseModel,
            {"call": {"a": "foo", "c": {"s": "bar", "i": 1}}},
        ),
        (  # response with a list
            "foo",
            {
                "call": [
                    {"a": "foo1", "c": {"s": "bar1", "i": 1}},
                    {"a": "foo2", "c": {"s": "bar2", "i": 2}},
                ]
            },
            BasemodelParentResponseModel,
            {
                "call": [
                    {"a": "foo1", "c": {"s": "bar1", "i": 1}},
                    {"a": "foo2", "c": {"s": "bar2", "i": 2}},
                ]
            },
        ),
    ],
)
def test_dict_encoder(
    call_base: str,
    response: dict,
    response_cls: type[BaseModel],
    expected_response_cls_instance: dict,
) -> None:
    assert dict_encoder(call_base, response, response_cls) == expected_response_cls_instance


@pytest.mark.parametrize(
    "encoder, call_base, response, response_cls",
    [
        pytest.param(dict_encoder, "test", "not a dict", None, id="dict_encoder"),
        pytest.param(json_encoder, "test", object, None, id="json_encoder"),
        pytest.param(
            basemodel_encoder,
            "test",
            {"test": {"s": "missing_i"}},
            BasemodelChildResponseModel,
            id="basemodel_encoder",
        ),
        pytest.param(
            dataclass_encoder,
            "test",
            {"test": {"s": "missing_i"}},
            BasemodelChildResponseModel,
            id="dataclass_encoder",
        ),
    ],
)
def test_encoder_exceptions(
    encoder: Callable[[str, dict | list[dict], type[BaseModel]], Any],
    call_base: str,
    response: Any,
    response_cls: type[BaseModel] | None,
):
    """
    Test bad responses to the parametrized encoder raises a EncoderResponseException
    """
    with pytest.raises(EncoderResponseException) as ex:
        result = encoder(call_base, response, response_cls)
