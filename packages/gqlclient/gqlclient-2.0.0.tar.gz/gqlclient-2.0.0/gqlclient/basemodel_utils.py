"""
Utilities for working with builtin dataclasses
"""

from dataclasses import is_dataclass
from types import NoneType
from types import UnionType
from typing import Annotated
from typing import ForwardRef
from typing import Generator
from typing import Union
from typing import get_args
from typing import get_origin
from typing import get_type_hints

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic._internal._model_construction import ModelMetaclass
from pydantic.fields import FieldInfo


def get_type(obj) -> type:
    """
    Get the type associated with an object.
    - For an instance, this will be the corresponding class.
    - For a class, this will be the class itself.
    - For a custom metaclass, this will be the custom metaclass itself.
    - For `type` (the default metaclass), this will be `type`.
    """
    # class and metaclass definitions are an instance of `type`, so the provided `obj` IS the class
    # otherwise, get the type of the instance, which will either be a class or metaclass definition
    return obj if isinstance(obj, type) else type(obj)


def is_basemodel(model: object) -> bool:
    """
    Return True if model is a BaseModel definition or a BaseModel instance
    """
    return isinstance(get_type(model), ModelMetaclass)


def is_union(tp: type) -> bool:
    """
    Return True if the passed type is a Union type via old style or new style.
      old style: Union[A, B] .
      new style:  A | B .
    """
    origin = get_origin(tp)
    # check new style via UnionType, check old style via Union
    return origin is UnionType or origin is Union


def is_optional(tp: type) -> bool:
    """
    Return True if the passed type is an Optional type via old style or new style.
      old style: Optional[A] or Union[A, None].
      new style:  A | None .
    """
    return is_union(tp) and type(None) in get_args(tp)


def get_referenced_type(t: ForwardRef) -> type:
    """
    get a reference to the specific ForwardRef class from its name and module
    :raises NameError: if ForwardRef module is not properly defined
    :raises RuntimeError: if t is not a ForwardRef
    """
    if not isinstance(t, ForwardRef):
        raise RuntimeError("Expected ForwardRef.  Received: type(t).__name__")

    # a dummy callable with a return type of t
    def _dummy(x) -> t: ...

    _dummy.__annotations__["return"] = t

    # now get the return type for the dummy callable
    referenced_type = get_type_hints(_dummy, globalns=globals(), localns=locals())["return"]
    return referenced_type


def extract_basemodel(t: type) -> type[BaseModel] | None:
    """
    Extract the BaseModel type from a nested BaseModel field.
    If no BaseModel is found, then None is returned.
    If multiple BaseModels are found, an exception is raised.
    If a pydantic or standard dataclass is found, an exception is raised.
    """
    if is_basemodel(t):
        return t  # noqa

    if is_dataclass(t):
        raise ValueError(f"Convert dataclass to a BaseModel.  Received dataclass: {t}")

    # eliminate unnecessary downstream processing for NoneType
    if t is NoneType:
        # NoneType is not a BaseModel, so return None.
        return None

    # the is_basemodel function does not catch ForwardRefs
    # Also, there is no way to detect a ForwardRef within a list unless the ForwardRef is explicitly declared
    # This is because quoted ForwardRefs within a list come in as a str, rather than a ForwardRef
    if isinstance(t, ForwardRef):
        # get a reference to the specific ForwardRef class from its name and module
        try:
            referenced_type = get_referenced_type(t)
            if is_basemodel(referenced_type):
                return referenced_type  # noqa noinspection PyTypeChecker
            if is_dataclass(referenced_type):
                raise ValueError(
                    f"Convert dataclass to a BaseModel.  Received ForwardRef to dataclass: {referenced_type}"
                )
            return None
        except NameError:
            # A NameError is expected if the ForwardRef module is not defined
            raise ValueError(
                f"Unable to instantiate {t}.  Ensure the ForwardRef module attribute is defined."
            )

    # old style Optional[type] and Union[type, None] are not caught above
    if is_optional(t):
        sub_type = next(iter(get_args(t)))
        # recurse into the sub-type for the Optional
        return extract_basemodel(sub_type)

    # Now deal with compound types
    origin = get_origin(t)

    if origin is None:
        # Not a compound type and already established that t is not a BaseModel, so return None.
        return None

    # handle Annotated types
    if origin is Annotated:
        sub_type = next(iter(get_args(t)))
        # recurse into the sub-type for the Annotated type
        return extract_basemodel(sub_type)

    # is_union necessary for old style Union[type1, type2]
    if is_union(t) or issubclass(origin, list | UnionType):
        sub_types = get_args(t)
        if not sub_types:
            raise RuntimeError(f"No args for '{t}' with origin {origin!r}.")
        if any(isinstance(sub_type, str) for sub_type in sub_types):
            raise ValueError(f"Explicit ForwardRef definition required within '{t}'")
        # recursion:  extract the BaseModel for each of the sub_types
        sub_type_basemodels = [extract_basemodel(sub_type) for sub_type in sub_types]
        if all(bm is None for bm in sub_type_basemodels):
            # No BaseModels found in the compound type
            return None
        found_basemodels = [bm for bm in sub_type_basemodels if bm is not None]
        if len(found_basemodels) != 1:
            raise ValueError(f"Unable to reconcile multiple BaseModels of '{t}'")
        return found_basemodels[0]

    raise RuntimeError(f"Unable to extract BaseModel for type '{t}'")


class FieldDefinition(BaseModel):
    # for FieldInfo
    model_config = ConfigDict(arbitrary_types_allowed=True)

    field_name: str
    field_info: FieldInfo


def yield_valid_fields(
    model: type[BaseModel], context: set[str] | str | None = None
) -> Generator[FieldDefinition, None, None]:
    """
    Yield all fields within the BaseModel.
    To avoid circular references, an exception is raised if previously visited BaseModels are encountered.
    """
    context = context or set()
    if isinstance(context, str):
        context = {context}

    if is_dataclass(model):
        raise ValueError(f"Convert dataclass to a BaseModel.  Received dataclass: {model}")

    for field_name, field_info in model.model_fields.items():
        field_type = field_info.annotation
        extracted_basemodel = extract_basemodel(field_type)

        # raise an exception if the BaseModel has been seen before
        if extracted_basemodel and extracted_basemodel.__name__ in context:
            # prevent infinite loop - raise exception
            raise ValueError(
                f"Circular Reference in {model.__name__!r} caused by {extracted_basemodel.__name__!r}"
            )

        yield FieldDefinition(field_name=field_name, field_info=field_info)
