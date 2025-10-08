"""
Tests for the blocking graphql_client library
"""

import pytest

from gqlclient import GraphQLClient


# Graphql Client to test
@pytest.fixture(scope="module")
def client() -> GraphQLClient:
    return GraphQLClient(gql_uri="http://localhost:5000/graphql")


def test_client_query_execution(client):
    pass
