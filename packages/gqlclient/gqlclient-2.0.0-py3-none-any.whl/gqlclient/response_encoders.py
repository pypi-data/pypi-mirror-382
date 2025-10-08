"""
Encoders for translating a dict graphql response into another form
"""

import json
import logging
from typing import Any
from typing import Callable
from typing import TypeAlias

from pydantic import BaseModel
from pydantic import TypeAdapter
from pydantic import ValidationError

from gqlclient.basemodel_utils import is_basemodel
from gqlclient.exceptions import EncoderResponseException

# warnings.deprecated was in typing-extensions prior to python 3.13
try:
    from warnings import deprecated
except ImportError:
    from typing_extensions import deprecated

__all__ = [
    "basemodel_encoder",
    "dataclass_encoder",
    "json_encoder",
    "dict_encoder",
    "ResponseEncoderSig",
]


logger = logging.getLogger(__name__)

ResponseEncoderSig: TypeAlias = Callable[[str, dict | list[dict], type[BaseModel]], Any]


@deprecated("Migrate from dataclass_encoder to basemodel_encoder.")
def dataclass_encoder(
    call_base: str,
    response: dict | list[dict],
    response_cls: type[BaseModel],
) -> BaseModel | list[BaseModel]:
    """
    Deprecated response encoder that produces a list or a single instance of the response class

    :param call_base: The base query or mutation the response is coming from
    :param response: The dict response from the graphql server
    :param response_cls: The BaseModel that specifies the structure of the graphql server response
    :return: An instance or list of instances of the response_cls instantiated with the graphql server response
    """
    return basemodel_encoder(call_base, response, response_cls)


def basemodel_encoder(
    call_base: str,
    response: dict | list[dict],
    response_cls: type[BaseModel],
) -> BaseModel | list[BaseModel]:
    """
    Response encoder that produces a list or a single instance of the response class

    :param call_base: The base query or mutation the response is coming from
    :param response: The dict response from the graphql server
    :param response_cls: The BaseModel that specifies the structure of the graphql server response
    :return: An instance or list of instances of the response_cls instantiated with the graphql server response
    :raises EncoderResponseException: Raised when the response for various BaseModel validation fails
    """

    if not is_basemodel(response_cls):
        message = f"'response_cls' must be a pydantic BaseModel. Found: {type(response_cls)}"
        raise EncoderResponseException(message)

    payload = response[call_base]
    try:
        if isinstance(payload, list):
            return TypeAdapter(list[response_cls]).validate_python(payload)
        if isinstance(payload, dict):
            return response_cls.model_validate(payload)
    except ValidationError as e:
        raise EncoderResponseException(f"Validation failed: {e}") from e
    raise EncoderResponseException(f"Unexpected payload type: {type(payload).__name__}")


def json_encoder(
    call_base: str,
    response: dict | list[dict],
    response_cls: type[BaseModel],
) -> str:
    """
    Response encoder that produces json string

    :param call_base: The base query or mutation the response is coming from
    :param response: The dict response from the graphql server
    :param response_cls: The BaseModel that specifies the structure of the graphql server response
    :return: A json formatted string of the response
    :raises EncoderResponseException: Raised when the response cannot be json serialized
    """
    try:
        result = json.dumps(response)
    except TypeError as e:
        logger.error(f"Error json encoding response: detail={e}")
        raise EncoderResponseException(str(e))
    return result


def dict_encoder(
    call_base: str,
    response: dict | list[dict],
    response_cls: type[BaseModel],
) -> dict | list[dict]:
    """
    Default encoder which returns the response as a dict or list of dicts

    :param call_base: The base query or mutation the response is coming from
    :param response: The dict response from the graphql server
    :param response_cls: The BaseModel that specifies the structure of the graphql server response
    :return: A json formatted string of the dict response
    :raises EncoderResponseException: Raised when the response is not a dict
    or list
    """
    if isinstance(response, (dict, list)):
        return response
    raise EncoderResponseException("Response parameter is expected to be a dict or list")
