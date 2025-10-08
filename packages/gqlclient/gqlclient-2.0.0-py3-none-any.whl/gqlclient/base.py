"""
Base class to support the creation of graphql queries and mutations.
"""

import json
import logging
from abc import ABC
from abc import abstractmethod
from typing import Any

from pydantic import BaseModel
from pydantic import ValidationError

from gqlclient.basemodel_utils import FieldDefinition
from gqlclient.basemodel_utils import extract_basemodel
from gqlclient.basemodel_utils import is_basemodel
from gqlclient.basemodel_utils import yield_valid_fields
from gqlclient.exceptions import GraphQLException
from gqlclient.exceptions import ModelException
from gqlclient.request_wrap import AbstractWrap
from gqlclient.request_wrap import StaticWrap
from gqlclient.request_wrap import dynamic_mutation_param_wrapper
from gqlclient.request_wrap import dynamic_query_param_wrapper
from gqlclient.response_encoders import ResponseEncoderSig
from gqlclient.response_encoders import basemodel_encoder

__all__ = ["GraphQLClientBase"]

logger = logging.getLogger(__name__)


class DefaultRequest(BaseModel):
    """
    Default request model that will pass type checking
    """


class GraphQLClientBase(ABC):
    """
    Abstract class for formatting and executing GraphQL queries and mutations

    :param gql_uri: Fully qualified URI for the graphQL endpoint.
    """

    def __init__(
        self,
        gql_uri: str,
        default_response_encoder: ResponseEncoderSig | None = basemodel_encoder,
    ):
        """
        Base constructor for the Graphql client
        :param gql_uri: URI for the graphql endpoint
        :param default_response_encoder: Optional encoder for graphql responses.  Default is basemodel_encoder.
        """
        self.gql_uri = gql_uri
        self.default_response_encoder = default_response_encoder

    @staticmethod
    def _graphql_response_from_model(model_cls: type[BaseModel]) -> str:
        """
        Generate a GraphQL Response query from the class for the response.

        :param model_cls: BaseModel class specifying the structure of the response from the graphql endpoint.

        :return: Portion of a graphql query which specifies the BaseModel response.
        """

        if not is_basemodel(model_cls):
            raise ModelException("Response model must be a pydantic BaseModel")

        def parse_field(
            field_def: FieldDefinition, context: set[str]
        ) -> str | tuple[str, list[str]] | None:
            """
            For a simple datatype, return the field name as a str.
            For a BaseModel, return a 2-tuple,
             with the first element being the field name
             and the second element being a list of the fields within the BaseModel.
            Nested BaseModels will result in recursion.
            """
            field_name = field_def.field_name
            field_info = field_def.field_info
            field_alias = field_info.serialization_alias or field_info.alias or field_name
            field_type = field_info.annotation
            extracted_basemodel = extract_basemodel(field_type)

            if not extracted_basemodel:
                return field_alias

            # each fork must have its own context to identify circular references specific to the branch
            branch_context = set(context)
            branch_context.add(extracted_basemodel.__name__)
            return (
                field_alias,
                [
                    parse_field(sub_field_def, branch_context)
                    for sub_field_def in yield_valid_fields(extracted_basemodel, branch_context)
                ],
            )

        def unpack(name: tuple[str, list[str]] | str) -> str:
            if not isinstance(name, tuple):
                return name
            # BaseModel name followed by its fields in curly braces
            return f"{name[0]} {{ {' '.join([unpack(n) for n in name[1]])} }}"

        root_context = {model_cls.__name__}
        names = [
            parse_field(field_def, root_context)
            for field_def in yield_valid_fields(model_cls, root_context)
        ]
        names = [unpack(name) for name in names]
        return ", ".join(names)

    @staticmethod
    def _encode_by_type(obj: object) -> str:
        """
        In most cases, encode with json.dumps.
        Special handling for dict.

        :param obj: data to be encoded

        :return: gql encoded value
        """

        match obj:
            case dict():
                # Sample dict input:  {'key_str':  'string', 'key_int': 42, 'key_bool': False, 'key_none': None}
                # Sample str output: {key_str:  "string", key_int: 42, key_bool: false, key_none: null}
                dict_str = "{"
                dict_str += ", ".join(
                    f"{k}: {GraphQLClientBase._encode_by_type(v)}" for k, v in obj.items()
                )  # noqa
                dict_str += "}"
                return dict_str
            case _:
                return json.dumps(obj)

    @staticmethod
    def _validate_model(model: BaseModel) -> None:
        """
        Validate an existing BaseModel instance.
        Necessary to address invalid data types.
        Unfortunately, model_dump silently sets invalid data types to None, so need to validate the model first.
        :param model: BaseModel to be validated
        :raises ValidationError: For an invalid BaseModel instance
        """

        # gather the data into a dict without using model_dump
        data = dict(model.__dict__)
        extra = getattr(model, "__pydantic_extra__", None)
        if extra:
            data.update(extra)

        # this will raise a ValidationError if the model is invalid
        model.model_validate(data)

    @staticmethod
    def _graphql_query_parameters_from_model(model: BaseModel) -> str:
        """
        Generate GraphQL query parameters from the BaseModel instance.

        :param model: BaseModel instance with the actual search values

        :return: Portion of a graphql query which specifies the query parameters
        """

        if not is_basemodel(model):
            raise ModelException("Parameter model must be a pydantic BaseModel")

        try:
            GraphQLClientBase._validate_model(model)
        except ValidationError as e:
            raise ModelException(f"Validation failed: {e}") from e

        # create query parameters for all parameters with values
        # `mode="json"` incorporates some simple conversions like datetime to ISO 8601 string
        data = model.model_dump(by_alias=True, exclude_none=True, mode="json")
        parameters = ", ".join(
            [
                f"{field_name}: {GraphQLClientBase._encode_by_type(field_value)}"
                for field_name, field_value in data.items()
            ]
        )
        return parameters

    @staticmethod
    def _get_param_wrapper(
        model: BaseModel,
        *,
        mutation_base: str | None = None,
    ) -> tuple[str, BaseModel]:
        """
        Return a GraphQL query param name and param values from the provided BaseModel instance.

        :param model: BaseModel instance with the actual request parameters
        :param mutation_base: Optional mutation name.  Must be provided for mutations using a dynamic param_name.

        :return: A 2-tuple:  The first element is the `param_name` and the second is a BaseModel with the `request` parameters.
        """

        if not is_basemodel(model):
            raise ModelException("Parameter model must be a pydantic BaseModel")

        if not isinstance(model, AbstractWrap):
            # simply passthrough the request as is
            return "", model

        if model.request_params is None:
            model.request_params = DefaultRequest()

        if isinstance(model, StaticWrap):
            # nest the request with the static param name provided
            return model.param_name, model.request_params

        # nest the request with a dynamic param name assigned by this client
        if mutation_base:
            return dynamic_mutation_param_wrapper(mutation_base), model.request_params
        return dynamic_query_param_wrapper(), model.request_params

    def get_query(
        self,
        query_base: str,
        query_response_cls: type[BaseModel],
        query_parameters: BaseModel | None = None,
    ) -> dict[str, str]:
        """
        Create a GraphQL formatted query string.

        :param query_base: Name of the root type to be queried
        :param query_response_cls: A BaseModel class specifying the structure of the response
        with attributes corresponding to the Graphql type and attribute names
        :param query_parameters: Optional. A BaseModel instance containing attributes corresponding
        to parameter names and values corresponding to the parameter value.

        :return: Dictionary that can be passed as json to the GraphQL API endpoint
        """

        # Construct graphql query
        gql_query = query_base
        query_parameters = query_parameters or DefaultRequest()
        param_wrapper, query_parameters = self._get_param_wrapper(query_parameters)
        parameters = self._graphql_query_parameters_from_model(query_parameters)
        if parameters and param_wrapper:
            # resulting format: (params: {id: "abc"})
            gql_query += f"({param_wrapper}: {{{parameters}}})"
        elif parameters:
            # resulting format: (id: "abc")
            gql_query += f"({parameters})"

        gql_query += f"{{{self._graphql_response_from_model(query_response_cls)}}}"
        return {"query": f"{{{gql_query} }}"}

    def get_mutation(
        self,
        mutation_base: str,
        mutation_parameters: BaseModel,
        mutation_response_cls: type[BaseModel],
    ) -> dict[str, str]:
        """
        Create a GraphQL formatted mutation string.

        :param mutation_base: Name of the root type to be mutated
        :param mutation_parameters: A BaseModel instance containing attributes corresponding to
        parameter names and values corresponding to the parameter value.
        :param mutation_response_cls: A BaseModel class specifying the response
               with attributes names and their data types.

        :return: Dictionary that can be passed as json to the GraphQL API endpoint
        """
        if mutation_response_cls is None:
            raise ValueError("A 'mutation_response_cls' is required.")

        # Construct graphql mutation
        gql_mutation = f"mutation {mutation_base} {{{mutation_base}"
        param_wrapper, mutation_parameters = self._get_param_wrapper(
            mutation_parameters, mutation_base=mutation_base
        )
        parameters = self._graphql_query_parameters_from_model(mutation_parameters)
        if param_wrapper:
            # resulting format: (params: {id: "abc"})
            gql_mutation += f"({param_wrapper}: {{{parameters}}})"
        else:
            # resulting format: (id: "abc")
            gql_mutation += f"({parameters})"

        gql_mutation += f"{{{self._graphql_response_from_model(mutation_response_cls)}}}"
        gql_mutation += " }"

        return {"query": f"{gql_mutation}", "operationName": mutation_base}

    @abstractmethod
    def execute_gql_call(self, query: dict, **kwargs) -> dict:
        """
        Executes a GraphQL query or mutation.

        :param query: Dictionary formatted graphql query

        :param kwargs: Optional arguments that the http client takes. e.g. headers

        :return: Dictionary containing the response from the GraphQL endpoint
        """

    def _format_response(
        self,
        query_base: str,
        response_cls: type[BaseModel],
        result: dict,
        response_encoder: ResponseEncoderSig | None = None,
    ) -> Any:
        """
        Helper function to format the graphql response using a provided encoder
        :param result: Graphql Response to format
        :param response_encoder: Encoder to use in formatting
        :return: depends on the response_encoder provided
        """
        if "errors" in result:
            raise GraphQLException(errors=result["errors"])
        if response_encoder is None:
            response_encoder = self.default_response_encoder
        return response_encoder(query_base, result["data"], response_cls)

    def execute_gql_query(
        self,
        query_base: str,
        query_response_cls: type[BaseModel],
        query_parameters: BaseModel | None = None,
        response_encoder: ResponseEncoderSig | None = None,
        **kwargs,
    ) -> Any:
        """
        Executes a graphql query based upon input BaseModels.

        :param query_base: Name of the root type to be queried

        :param query_parameters: Optional. A BaseModel instance containing attributes corresponding to
        parameter names and values corresponding to the parameter value.

        :param query_response_cls: A BaseModel class specifying the structure of the response
        with attributes corresponding to the Graphql type and attribute names

        :param response_encoder: A callable which takes a dict graphql response and returns a reformatted type

        :param kwargs: Optional arguments that http client (`requests`) takes. e.g. headers


        :return: The response formatted by the specified response_encoder.  Default is basemodel_encoder.
        """
        query_parameters = query_parameters or DefaultRequest()
        query = self.get_query(query_base, query_response_cls, query_parameters)
        result = self.execute_gql_call(query, **kwargs)
        return self._format_response(query_base, query_response_cls, result, response_encoder)

    def execute_gql_mutation(
        self,
        mutation_base: str,
        mutation_parameters: BaseModel,
        mutation_response_cls: type[BaseModel],
        response_encoder: ResponseEncoderSig | None = None,
        **kwargs,
    ) -> Any:
        """
        Executes a graphql mutation based upon input BaseModels.

        :param mutation_base: Name of the root type to be mutated

        :param mutation_parameters: A BaseModel instance containing attributes corresponding to
        parameter names and values corresponding to the parameter value.

        :param mutation_response_cls: A BaseModel class specifying the response
               with attributes names and their data types.

        :param response_encoder: A callable which takes the following arguments:
            str for the base type call e.g. query_base or mutation_base
            dict for the data returned in under the 'data' key
            BaseModel that structured the response

        :param kwargs: Optional arguments that http client (`requests`) takes. e.g. headers

        :return: The response formatted by the specified response_encoder.  Default is basemodel_encoder.
        """
        mutation = self.get_mutation(mutation_base, mutation_parameters, mutation_response_cls)
        result = self.execute_gql_call(mutation, **kwargs)
        return self._format_response(mutation_base, mutation_response_cls, result, response_encoder)

    def __str__(self):
        return f"GraphQLClient(gql_uri={self.gql_uri}, default_response_encoder={self.default_response_encoder})"

    def __repr__(self):
        return str(self)
