"""
Test basemodel_utils advanced functions:  extract_basemodel and yield_valid_fields
"""

from dataclasses import dataclass
from typing import Annotated
from typing import Any
from typing import ForwardRef
from typing import Optional
from typing import Union

import pytest
from pydantic import BaseModel
from pydantic import Strict
from pydantic.dataclasses import dataclass as pydantic_dataclass

from gqlclient.basemodel_utils import extract_basemodel
from gqlclient.basemodel_utils import yield_valid_fields

# valid explicit forward references
BuiltinRef = ForwardRef("Builtin", module=__name__)
PydanticRef = ForwardRef("Pydantic", module=__name__)
BasemodelRef = ForwardRef("Basemodel", module=__name__)


@dataclass
class BuiltinWithForwardRef:
    parent_ref: list[BuiltinRef]
    value: str = "builtin with forward ref"


@dataclass
class Builtin:
    child_ref: BuiltinWithForwardRef
    value: str = "builtin dataclass"


@pydantic_dataclass
class PydanticWithForwardRef:
    parent_ref: list[PydanticRef]
    value: str = "pydantic with forward ref"


@pydantic_dataclass
class Pydantic:
    child_ref: PydanticWithForwardRef
    value: str = "pydantic"


class BasemodelWithForwardRef(BaseModel):
    parent_ref: list[BasemodelRef]
    value: str = "basemodel with forward ref"


class SimpleBasemodel(BaseModel):
    str_param: str
    int_param: int
    bool_param: bool
    bytes_param: bytes
    float_param: float


class BasemodelWithChild(BaseModel):
    name: str | None = "parent"
    child: SimpleBasemodel


class Basemodel(BaseModel):
    child_ref: BasemodelWithForwardRef
    value: str | None = "basemodel"


class BasemodelWithAnnotatedTypes(BaseModel):
    strict_str: Annotated[str, Strict()]
    strict_int: Annotated[int, Strict()]
    strict_bool: Annotated[bool, Strict()]
    strict_bytes: Annotated[bytes, Strict()]
    strict_float: Annotated[float, Strict()]
    annotated_dc: Annotated[Basemodel, "neglected meta"]
    value: str = "basemodel with annotated types"


@pytest.mark.parametrize(
    "test_type, expected_result",
    [
        pytest.param(Optional[str], None, id="old_opt"),
        pytest.param(Union[str, None], None, id="old_union"),
        pytest.param(str | None, None, id="new_union"),
        pytest.param(str, None, id="str"),
        pytest.param(str | bool, None, id="str_bool"),
        pytest.param(Annotated[str, "metadata"], None, id="annotated_str"),
        pytest.param(Annotated[int, "metadata"], None, id="annotated_int"),
        pytest.param(Annotated[bool, "metadata"], None, id="annotated_bool"),
        pytest.param(Basemodel | bool, Basemodel, id="new_basemodel_bool"),
        pytest.param(Basemodel | None, Basemodel, id="new_basemodel_none"),
        pytest.param(Union[Basemodel, bool], Basemodel, id="old_basemodel_bool"),
        pytest.param(Union[Basemodel, None], Basemodel, id="old_basemodel_none"),
        pytest.param(Annotated[Basemodel, "metadata"], Basemodel, id="annotated_basemodel"),
    ],
)
def test_extract_basemodel_simple(test_type: type, expected_result: Any):
    """Verify proper BaseModel extraction"""
    assert extract_basemodel(test_type) == expected_result


@pytest.mark.parametrize(
    "test_type",
    [
        pytest.param(SimpleBasemodel | Basemodel, id="new_basemodel_basemodel"),
        pytest.param(Union[SimpleBasemodel, Basemodel], id="old_basemodel_basemodel"),
        pytest.param(Builtin | Pydantic, id="new_builtin_pyd"),
        pytest.param(Union[Builtin, Pydantic], id="old_builtin_pyd"),
        pytest.param(Pydantic | Basemodel, id="new_pyd_basemodel"),
        pytest.param(Union[Pydantic, Basemodel], id="old_pyd_basemodel"),
        pytest.param(Builtin | Basemodel, id="new_builtin_basemodel"),
        pytest.param(Union[Builtin, Basemodel], id="old_builtin_basemodel"),
    ],
)
def test_extract_basemodel_multi(test_type: type):
    """Raise exception when a field has multiple possible dataclasses"""
    with pytest.raises(ValueError):
        extract_basemodel(test_type)


@pytest.mark.parametrize(
    "test_type, expected_result",
    [
        pytest.param(BasemodelRef, Basemodel, id="basemodel"),
        pytest.param(Optional[BasemodelRef], Basemodel, id="opt_basemodel"),
        pytest.param(Union[BasemodelRef, None], Basemodel, id="union_basemodel"),
        pytest.param(list[BasemodelRef], Basemodel, id="list_basemodel"),
        pytest.param(list[Optional[BasemodelRef]], Basemodel, id="list_opt_basemodel"),
        pytest.param(list[Union[BasemodelRef, bool]], Basemodel, id="list_union_basemodel"),
    ],
)
def test_extract_basemodel_forward_ref_explicit_basemodel(
    test_type: type, expected_result: BaseModel
):
    """Verify proper BaseModel extraction from ForwardRefs"""
    actual_result = extract_basemodel(test_type)
    # actual result will be a builtin (annotated) dataclass, not a BaseModel
    assert actual_result == expected_result


@pytest.mark.parametrize(
    "test_type",
    [
        pytest.param(Optional["Basemodel"], id="opt_basemodel"),
        pytest.param(Union["Basemodel", None], id="union_basemodel"),
        pytest.param(list["Basemodel"], id="list_basemodel"),
        pytest.param(list[Optional["Basemodel"]], id="list_opt_basemodel"),
        pytest.param(list[Union["Basemodel", bool]], id="list_union_basemodel"),
    ],
)
def test_extract_basemodel_forward_ref_implicit(test_type: type):
    """Verify error if an implicit ForwardRef is wrapped by another data type"""
    with pytest.raises(ValueError):
        extract_basemodel(test_type)


@pytest.mark.parametrize(
    "test_type",
    [
        pytest.param(ForwardRef("Basemodel"), id="basemodel_none"),
        pytest.param(ForwardRef("Basemodel", module="abc"), id="basemodel_abc"),
    ],
)
def test_extract_basemodel_forward_ref_module(test_type: type):
    """Verify error if ForwardRef has missing or invalid module attribute"""
    with pytest.raises(ValueError):
        extract_basemodel(test_type)


@pytest.mark.parametrize(
    "test_type",
    [
        pytest.param(BuiltinRef, id="builtin"),
        pytest.param(PydanticRef, id="pydantic"),
    ],
)
def test_extract_basemodel_forward_ref_dataclass(test_type: type):
    """Verify error if ForwardRef is to a dataclass"""
    with pytest.raises(ValueError):
        extract_basemodel(test_type)


@pytest.mark.parametrize(
    "test_type, test_context, expected_result",
    [
        pytest.param(
            SimpleBasemodel,
            None,
            {"str_param", "int_param", "bool_param", "bytes_param", "float_param"},
            id="basemodel_simple",
        ),
        pytest.param(BasemodelWithChild, None, {"name", "child"}, id="basemodel_with_child"),
        pytest.param(
            BasemodelWithForwardRef,
            None,
            {"parent_ref", "value"},
            id="basemodel_with_forward_ref",
        ),
        pytest.param(Basemodel, None, {"child_ref", "value"}, id="basemodel_with_child_ref"),
        pytest.param(
            BasemodelWithAnnotatedTypes,
            None,
            {
                "strict_str",
                "strict_int",
                "strict_bool",
                "strict_bytes",
                "strict_float",
                "annotated_dc",
                "value",
            },
            id="basemodel_annotated",
        ),
    ],
)
def test_yield_valid_fields(
    test_type: type[BaseModel],
    test_context: set[str] | str | None,
    expected_result: set[str],
):
    """Verify the fields of the dataclass are returned"""
    fields = set()
    for field_def in yield_valid_fields(test_type, test_context):
        fields.add(field_def.field_name)
    assert fields == expected_result


@pytest.mark.parametrize(
    "test_type",
    [
        pytest.param(Builtin, id="builtin"),
        pytest.param(Pydantic, id="pydantic"),
    ],
)
def test_yield_valid_fields_dataclass(test_type: type):
    """Verify error for dataclass"""
    test_context = None
    with pytest.raises(ValueError):
        list(yield_valid_fields(test_type, test_context))


@pytest.mark.parametrize(
    "test_type, test_context",
    [
        pytest.param(
            Basemodel,
            "BasemodelWithForwardRef",
            id="basemodel_parent_context",
        ),
        pytest.param(
            BasemodelWithForwardRef,
            {"Basemodel"},
            id="basemodel_child_context",
        ),
    ],
)
def test_yield_valid_fields_circular(
    test_type: type[BaseModel],
    test_context: set[str] | str | None,
):
    """Verify an exception is raised to avoid infinite recursion caused by circular references"""
    with pytest.raises(ValueError):
        fields = set()
        for field_def in yield_valid_fields(test_type, test_context):
            fields.add(field_def.field_name)
