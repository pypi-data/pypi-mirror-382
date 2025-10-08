"""
This client can handle three possible request models:
  1.  A direct passthrough of the BaseModel request to the GQL server without modification, for example: (id: "abc")
  2.  A nested, or wrapped, BaseModel request inside a mapping, for example: (params: {id: "abc"})
  2.a.  The client can dynamically assign the `params` key
  2.b.  The caller can define the static `params` key
This module provides tooling for wrapping requests.
If the caller desires a direct passthrough of the BaseModel request, this module should not be used.
"""

from abc import ABC

from pydantic import BaseModel
from pydantic import field_validator

from gqlclient.basemodel_utils import is_basemodel


class AbstractWrap(BaseModel, ABC):
    """
    Abstract BaseModel for nested request params.
    """

    request_params: BaseModel | None = None

    # Allow for other BaseModels
    # model_config = ConfigDict(arbitrary_types_allowed=True)

    def __new__(cls, *args, **kwargs):
        if cls == AbstractWrap:
            raise TypeError("AbstractWrap cannot be instantiated because it is an abstract class")
        return super().__new__(cls)

    # Enforce that request_params is a BaseModel instance (or None)
    # Yes, this is a classmethod
    @field_validator("request_params", mode="before")
    def _validate_request_params(cls, v: BaseModel | None):
        if v is None:
            return v
        if is_basemodel(v):
            return v
        raise TypeError(f"'request_params' must be a pydantic BaseModel. Found: {type(v)}")


class DynamicWrap(AbstractWrap):
    """
    Concrete BaseModel for nested request params with a dynamic param name.
    """

    # request_params is redeclared here to solely to eliminate IDE type checking errors
    # request_params is inherited from AbstractWrap, so this is not technically necessary
    request_params: BaseModel | None = None


class StaticWrap(AbstractWrap):
    """
    Concrete BaseModel for nested request params with a static param name.
    """

    # request_params is redeclared here to solely to eliminate IDE type checking errors
    # request_params is inherited from AbstractWrap, so this is not technically necessary
    request_params: BaseModel | None = None
    param_name: str


def wrap_request(
    request_params: BaseModel | None = None,
    *,
    param_name: str | None = None,
) -> DynamicWrap | StaticWrap:
    """
    Return a nested, or wrapped, request BaseModel.
    :param request_params: A BaseModel instance to be nested.
    :param param_name: Optional.  If provided, this will be the mapping key.
    Otherwise the mapping key will be dynamically generated at a later point.
    :return: A nested BaseModel with `request_params` matching the input.
    If `param_name` was provided, the returned BaseModel will have a `param_name` field matching the input.
    """
    if request_params is not None:
        if not is_basemodel(request_params):
            message = (
                f"'request_params' must be a pydantic BaseModel. Found: {type(request_params)}"
            )
            raise TypeError(message)
        if isinstance(request_params, type):
            raise TypeError("The pydantic BaseModel for 'request_params' must be instantiated")

    if isinstance(param_name, str):
        return StaticWrap(request_params=request_params, param_name=param_name)
    return DynamicWrap(request_params=request_params)


def dynamic_mutation_param_wrapper(mutation_name: str) -> str:
    """
    Server side convention for DKIST:
     - create mutations wrap request params with `createParams`
     - update mutations wrap request params with `updateParams`
     - delete mutations wrap request params with `deleteParams`
    """
    if not mutation_name:
        raise ValueError(f"Unable to determine param_wrapper")

    # this works because update, create and delete are all 6 characters
    return f"{mutation_name[:6]}Params"


def dynamic_query_param_wrapper() -> str:
    """
    Server side convention for DKIST:
     - retrieval queries wrap request params with `filterParams`
    """
    return "filterParams"
