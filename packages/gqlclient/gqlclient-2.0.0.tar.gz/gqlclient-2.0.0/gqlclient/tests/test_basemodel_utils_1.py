"""
Test basemodel_utils core functions:  get_type, is_basemodel, is_union and is_optional
"""

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from types import NoneType
from typing import Annotated
from typing import Any
from typing import ForwardRef
from typing import Optional
from typing import Union

import pytest
from pydantic import BaseModel
from pydantic import Field
from pydantic import Strict
from pydantic.dataclasses import dataclass as pydantic_dataclass

from gqlclient.basemodel_utils import get_type
from gqlclient.basemodel_utils import is_basemodel
from gqlclient.basemodel_utils import is_optional
from gqlclient.basemodel_utils import is_union

# valid explicit forward references
BuiltinRef = ForwardRef("Builtin", module=__name__)
PydanticRef = ForwardRef("Pydantic", module=__name__)
BasemodelRef = ForwardRef("Basemodel", module=__name__)


@dataclass
class Builtin:
    str_param: str
    int_param: int
    float_param: float
    str_array_param: list[str]
    num_array_param: list[int]
    bool_param: bool
    date_param: datetime
    optional_int_param: int | None = None
    optional_list_param: list[str] | None = field(default_factory=list)


builtin = Builtin(
    str_param="A",
    int_param=1,
    float_param=1.1,
    str_array_param=["A", "B"],
    num_array_param=[1, 2],
    bool_param=False,
    date_param=datetime.strptime("2010-03-25T14:08:00", "%Y-%m-%dT%H:%M:%S"),
)


@pydantic_dataclass
class Pydantic:
    str_param: str
    int_param: int
    float_param: float
    str_array_param: list[str]
    num_array_param: list[int]
    bool_param: bool
    date_param: datetime
    optional_int_param: int | None = None
    optional_list_param: list[str] | None = Field(default_factory=list)


class Basemodel(BaseModel):
    str_param: str
    int_param: int
    float_param: float
    str_array_param: list[str]
    num_array_param: list[int]
    bool_param: bool
    date_param: datetime
    optional_int_param: int | None = None
    optional_list_param: list[str] | None = Field(default_factory=list)


@dataclass
class BuiltinWithAnnotatedTypes:
    strict_str: Annotated[str, Strict()]
    strict_int: Annotated[int, Strict()]
    strict_bool: Annotated[bool, Strict()]
    strict_bytes: Annotated[bytes, Strict()]
    strict_float: Annotated[float, Strict()]
    annotated_dc: Annotated[Builtin, "interesting metadata"]
    value: str = "builtin with annotated types"


@pydantic_dataclass
class PydanticWithAnnotatedTypes:
    strict_str: Annotated[str, Strict()]
    strict_int: Annotated[int, Strict()]
    strict_bool: Annotated[bool, Strict()]
    strict_bytes: Annotated[bytes, Strict()]
    strict_float: Annotated[float, Strict()]
    annotated_dc: Annotated[Pydantic, "boring meta"]
    value: str = "pydantic with annotated types"


class BasemodelWithAnnotatedTypes(BaseModel):
    strict_str: Annotated[str, Strict()]
    strict_int: Annotated[int, Strict()]
    strict_bool: Annotated[bool, Strict()]
    strict_bytes: Annotated[bytes, Strict()]
    strict_float: Annotated[float, Strict()]
    annotated_dc: Annotated[Basemodel, "neglected meta"]
    value: str = "basemodel with annotated types"


pydantic = Pydantic(
    str_param="A",
    int_param=1,
    float_param=1.1,
    str_array_param=["A", "B"],
    num_array_param=[1, 2],
    bool_param=False,
    date_param=datetime.strptime("2010-03-25T14:08:00", "%Y-%m-%dT%H:%M:%S"),
)

basemodel = Basemodel(
    str_param="A",
    int_param=1,
    float_param=1.1,
    str_array_param=["A", "B"],
    num_array_param=[1, 2],
    bool_param=False,
    date_param=datetime.strptime("2010-03-25T14:08:00", "%Y-%m-%dT%H:%M:%S"),
)


@pytest.mark.parametrize(
    "test_type, expected_result",
    [
        pytest.param(type, type, id="type"),
        pytest.param(object, object, id="object"),
        pytest.param(object(), object, id="object_instance"),
        pytest.param(None, NoneType, id="None"),
        pytest.param(NoneType, NoneType, id="NoneType"),
        pytest.param(int, int, id="int"),
        pytest.param(42, int, id="int_instance"),
        pytest.param(Builtin, Builtin, id="builtin_definition"),
        pytest.param(builtin, Builtin, id="builtin_instance"),
        pytest.param(BuiltinRef, ForwardRef, id="builtin_forward_ref"),
        pytest.param(Pydantic, Pydantic, id="pydantic_definition"),
        pytest.param(pydantic, Pydantic, id="pydantic_instance"),
        pytest.param(PydanticRef, ForwardRef, id="pydantic_forward_ref"),
        pytest.param(BaseModel, BaseModel, id="the_basemodel"),
        pytest.param(Basemodel, Basemodel, id="basemodel_definition"),
        pytest.param(basemodel, Basemodel, id="basemodel_instance"),
        pytest.param(BasemodelRef, ForwardRef, id="basemodel_forward_ref"),
    ],
)
def test_get_type(test_type: type, expected_result: Any):
    assert get_type(test_type) == expected_result


@pytest.mark.parametrize(
    "test_type, expected_result",
    [
        pytest.param(type, False, id="type"),
        pytest.param(object, False, id="object"),
        pytest.param(object(), False, id="object_instance"),
        pytest.param(None, False, id="None"),
        pytest.param(NoneType, False, id="NoneType"),
        pytest.param(int, False, id="int"),
        pytest.param(42, False, id="int_instance"),
        pytest.param(Builtin, False, id="builtin_definition"),
        pytest.param(builtin, False, id="builtin_instance"),
        pytest.param(BuiltinRef, False, id="builtin_forward_ref"),
        pytest.param(Pydantic, False, id="pydantic_definition"),
        pytest.param(pydantic, False, id="pydantic_instance"),
        pytest.param(PydanticRef, False, id="pydantic_forward_ref"),
        pytest.param(Basemodel, True, id="basemodel_definition"),
        pytest.param(basemodel, True, id="basemodel_instance"),
        pytest.param(BasemodelRef, False, id="basemodel_forward_ref"),
    ],
)
def test_is_basemodel(test_type: type, expected_result: Any):
    """Properly identify BaseModel definitions and instances"""
    assert is_basemodel(test_type) == expected_result


@pytest.mark.parametrize(
    "test_type, expected_result",
    [
        pytest.param(Optional[str], True, id="old_opt"),
        pytest.param(Union[str, None], True, id="old_union"),
        pytest.param(str | None, True, id="new_union"),
        pytest.param(str, False, id="str"),
        pytest.param(str | bool, True, id="str_bool"),
        pytest.param(Builtin | bool, True, id="new_builtin_bool"),
        pytest.param(Builtin | None, True, id="new_builtin_none"),
        pytest.param(Union[Builtin, bool], True, id="old_builtin_bool"),
        pytest.param(Union[Builtin, None], True, id="old_builtin_none"),
        pytest.param(Pydantic | bool, True, id="new_pyd_bool"),
        pytest.param(Pydantic | None, True, id="new_pyd_none"),
        pytest.param(Union[Pydantic, bool], True, id="old_pyd_bool"),
        pytest.param(Union[Pydantic, None], True, id="old_pyd_none"),
        pytest.param(Builtin | Pydantic, True, id="new_builtin_pyd"),
        pytest.param(Union[Builtin, Pydantic], True, id="old_builtin_pyd"),
        pytest.param(Basemodel | bool, True, id="new_basemodel_bool"),
        pytest.param(Basemodel | None, True, id="new_basemodel_none"),
        pytest.param(Union[Basemodel, bool], True, id="old_basemodel_bool"),
        pytest.param(Union[Basemodel, None], True, id="old_basemodel_none"),
        pytest.param(Builtin | Basemodel, True, id="new_builtin_basemodel"),
        pytest.param(Union[Builtin, Basemodel], True, id="old_builtin_basemodel"),
    ],
)
def test_is_union(test_type: type, expected_result: bool):
    assert is_union(test_type) == expected_result


@pytest.mark.parametrize(
    "test_type, expected_result",
    [
        pytest.param(Optional[str], True, id="old_opt"),
        pytest.param(Union[str, None], True, id="old_union"),
        pytest.param(str | None, True, id="new_union"),
        pytest.param(str, False, id="str"),
        pytest.param(str | bool, False, id="str_bool"),
        pytest.param(Builtin | bool, False, id="new_builtin_bool"),
        pytest.param(Builtin | None, True, id="new_builtin_none"),
        pytest.param(Union[Builtin, bool], False, id="old_builtin_bool"),
        pytest.param(Union[Builtin, None], True, id="old_builtin_none"),
        pytest.param(Pydantic | bool, False, id="new_pyd_bool"),
        pytest.param(Pydantic | None, True, id="new_pyd_none"),
        pytest.param(Union[Pydantic, bool], False, id="old_pyd_bool"),
        pytest.param(Union[Pydantic, None], True, id="old_pyd_none"),
        pytest.param(Builtin | Pydantic, False, id="new_builtin_pyd"),
        pytest.param(Union[Builtin, Pydantic], False, id="old_builtin_pyd"),
        pytest.param(Basemodel | bool, False, id="new_basemodel_bool"),
        pytest.param(Basemodel | None, True, id="new_basemodel_none"),
        pytest.param(Union[Basemodel, bool], False, id="old_basemodel_bool"),
        pytest.param(Union[Basemodel, None], True, id="old_basemodel_none"),
        pytest.param(Builtin | Basemodel, False, id="new_builtin_basemodel"),
        pytest.param(Union[Builtin, Basemodel], False, id="old_builtin_basemodel"),
    ],
)
def test_is_optional(test_type: type, expected_result: bool):
    assert is_optional(test_type) == expected_result
