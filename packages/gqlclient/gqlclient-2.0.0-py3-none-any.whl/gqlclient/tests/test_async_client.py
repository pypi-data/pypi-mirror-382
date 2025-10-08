"""
Tests for the async graphql_client library
"""

import pytest

from gqlclient.async_client import AsyncGraphQLClient


# Graphql Client to test
# This test requires [async] pip install
@pytest.fixture(scope="module")
def client() -> AsyncGraphQLClient:
    return AsyncGraphQLClient(gql_uri="http://localhost:5000/graphql")


def test_async_client_query_execution(client):
    pass
