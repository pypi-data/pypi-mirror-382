"""
Define NULL which can be passed as a request argument.
"""

# The inspiration for NULL was drawn from UNSET in the strawberry library.
# The intrepid developer will find striking code similarities between NULL and UNSET.
# NULL and UNSET serve inverse purposes.
from typing import Any
from typing import Optional

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

# Self was in typing-extensions prior to python 3.11
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self


class NullType:
    __instance: Optional[Self] = None

    def __new__(cls: type[Self], *args, **kwargs) -> Self:
        """singleton"""
        if cls.__instance is None:
            ret = super().__new__(cls)
            cls.__instance = ret
            return ret
        else:
            return cls.__instance

    def __str__(self) -> str:
        """Returns 'null' which is needed for json serialization"""
        return "null"

    def __repr__(self) -> str:
        return "NULL"

    def __bool__(self) -> bool:
        return False

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Self, handler: GetCoreSchemaHandler):
        """
        Validation (input) and serialization (output) rules for pydantic V2 BaseModel.
        The handler is provided by the pydantic V2 framework.
        The method returns a pydantic_core.CoreSchema to the pydantic V2 framework.
        """
        if source_type is not NullType:
            raise ValueError("This validation is only for NullType")

        # serialization on output
        def serialize_null_type(v: Self) -> None:
            # for both info.mode = "python" and info.mode = "json"
            return None

        # The validator part roughly equates to: `isinstance(input_value, NullType)`.
        return core_schema.is_instance_schema(
            cls=NullType,
            cls_repr="NullType",
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize_null_type,
                info_arg=False,
                when_used="always",
                return_schema=core_schema.none_schema(),
            ),
        )


NULL: Any = NullType()

__all__ = [
    "NULL",
]
