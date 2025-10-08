"""
Implementation of the Base graphql client to support the asynchronous creation and
execution of graphql queries and mutations
"""

import logging
from typing import Any

import aiohttp
from pydantic import BaseModel

from gqlclient.base import DefaultRequest
from gqlclient.base import GraphQLClientBase
from gqlclient.exceptions import ClientErrorException
from gqlclient.exceptions import RedirectionResponseException
from gqlclient.exceptions import ServerConnectionException
from gqlclient.exceptions import ServerErrorException
from gqlclient.exceptions import ServerResponseException

__all__ = ["AsyncGraphQLClient"]

from gqlclient.response_encoders import ResponseEncoderSig

logger = logging.getLogger(__name__)


class AsyncGraphQLClient(GraphQLClientBase):
    """
    Helper class for formatting and executing asynchronous GraphQL queries and mutations

    """

    async def execute_gql_call(self, query: dict, **kwargs) -> dict:
        """
        Executes a GraphQL query or mutation using aiohttp.

        :param query: Dictionary formatted graphql query.

        :param kwargs: Optional arguments that `aiohttp` takes. e.g. headers

        :return: Dictionary containing the response from the GraphQL endpoint.
        """

        logger.debug(f"Executing graphql call: host={self.gql_uri}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.gql_uri, json=query, **kwargs) as response:
                    result = await response.json()
                    if response.status > 299:
                        exception_message = (
                            f"Server returned invalid response: " f"code=HTTP{response.status}, "
                        )
                        if response.status > 499:
                            raise ServerErrorException(exception_message)
                        if response.status > 399:
                            raise ClientErrorException(exception_message)
                        raise RedirectionResponseException(exception_message)
            except aiohttp.ClientConnectionError as e:
                logger.error(
                    f"Error connecting to graphql server: server={self.gql_uri}, detail={e!r}"
                )
                raise ServerConnectionException(
                    f"Error connecting to graphql server: server={self.gql_uri}, detail={e!r}"
                ) from e
            except aiohttp.ContentTypeError as e:
                logger.error(
                    f"Error decoding response from graphql server: "
                    f"server={self.gql_uri}, "
                    f"detail={e}"
                )
                raise ServerResponseException(
                    f"Error decoding response from graphql server: "
                    f"server={self.gql_uri}, "
                    f"detail={e}"
                )
            return result

    async def execute_gql_query(
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

        :param query_response_cls: A BaseModel class representing the structure of the response
        object with attributes corresponding to the Graphql type and attribute names

        :param response_encoder: A callable which takes a dict graphql response and returns a reformatted type

        :param kwargs: Optional arguments that `aiohttp` takes. e.g. headers

        :return: The response formatted by the specified response_encoder.  Default is basemodel_encoder.
        """
        query_parameters = query_parameters or DefaultRequest()
        query = self.get_query(query_base, query_response_cls, query_parameters)
        result = await self.execute_gql_call(query, **kwargs)
        return self._format_response(query_base, query_response_cls, result, response_encoder)

    async def execute_gql_mutation(
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
            dict for the data returned in the 'data' key
            BaseModel that structured the response

        :param kwargs: Optional arguments that `aiohttp` takes. e.g. headers

        :return: The response formatted by the specified response_encoder.  Default is basemodel_encoder.
        """
        mutation = self.get_mutation(mutation_base, mutation_parameters, mutation_response_cls)
        result = await self.execute_gql_call(mutation, **kwargs)
        return self._format_response(mutation_base, mutation_response_cls, result, response_encoder)
