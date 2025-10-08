gqlclient
=========

|codecov|

.. image:: https://readthedocs.org/projects/graphql-client/badge/?version=latest
   :target: https://dkistdc.readthedocs.io/projects/graphql-client/en/latest/?badge=latest
   :alt: Documentation Status

A pythonic interface for making requests to a GraphQL server using
pydantic V2 BaseModels to spare you from string manipulation.

Features
--------

-  Use `pydantic <https://pypi.org/project/pydantic/>`__ v2 BaseModels to
   specify graphql parameters and responses

-  As of gqlclient v2, standard library dataclasses are no longer supported

-  As of gqlclient v2, pydantic dataclasses are no longer supported

-  Create and execute GraphQL Queries based upon typed models

-  Create and execute GraphQL Mutations based upon typed models

-  Async support

Installation
------------

.. code:: bash

   pip install gqlclient

with ``asyncio`` support

.. code:: bash

   pip install gqlclient[async]

for developers

.. code:: bash

   pip install gqlclient[test]
   pip install pre-commit
   pre-commit install

Examples
--------

**Query**

.. code:: python

   # limited to pydantic V2
   from pydantic import BaseModel

   from gqlclient import GraphQLClient
   from gqlclient.request_wrap import wrap_request
   from gqlclient.response_encoders import json_encoder

   class GetRequest(BaseModel):
       attr_one: str
       attr_two: int

   class Response(BaseModel):
       attr_three: int
       attr_four: str

   # url for a running GQL server
   client = GraphQLClient(gql_uri="http://localhost:8080/graphql")
   query_params = GetRequest(attr_one="foo", attr_two=3)
   query = client.get_query(query_base="baseType", query_response_cls=Response, query_parameters=wrap_request(query_params))
   print(query)
   # {'query': '{baseType(filterParams: {attr_one: "foo", attr_two: 3}){attr_three, attr_four} }'}
   pseudo_response = client.execute_gql_query(query_base="baseType", query_response_cls=Response, query_parameters=wrap_request(query_params))
   print(pseudo_response)
   # [Response(attr_three=5, attr_four="bar")]

**Mutation**

.. code:: python

   # limited to pydantic V2
   from pydantic import BaseModel

   from gqlclient import GraphQLClient


   class MutationRequest(BaseModel):
       attr_one: str
       attr_two: int


   class Response(BaseModel):
       attr_three: int
       attr_four: str

   # url for a running GQL server
   client = GraphQLClient(gql_uri="http://localhost:8080/graphql")
   mutation_params = MutationRequest(attr_one="foo", attr_two=3)
   mutation = client.get_mutation(mutation_base="baseMutation", mutation_response_cls=Response, mutation_parameters=wrap_request(mutation_params))
   print(mutation)
   # {'query': 'mutation baseMutation {baseMutation(baseMuParams: {attr_one: "foo", attr_two: 3}){attr_three, attr_four} }', 'operationName': 'baseMutation'}

   pseudo_response = client.execute_gql_mutation(mutation_base="baseMutation", mutation_response_cls=Response, mutation_parameters=wrap_request(mutation_params))
   print(pseudo_response)
   # [Response(attr_three=5, attr_four="bar")]

**Encoders**

.. code:: python

   # limited to pydantic V2
   from pydantic import BaseModel

   from gqlclient import GraphQLClient
   from gqlclient import json_encoder

   # url for a running GQL server
   # set the default encoder to the json_encoder
   client = GraphQLClient(gql_uri="http://localhost:8080/graphql", default_response_encoder=json_encoder)

   class QueryResponse(BaseModel):
       workflowId: int
       workflowName: str
       workflowDescription: str | None = None

   response = client.execute_gql_query("workflows",QueryResponse)
   print(response)
   # Response is a json formatted string
   # {"workflows": [{"workflowId": 1, "workflowName": "gql3_full - workflow_name", "workflowDescription": "gql3_full - workflow_description"}, {"workflowId": 2, "workflowName": "VBI base calibration", "workflowDescription": "The base set of calibration tasks for VBI."}]}

   from gqlclient import basemodel_encoder
   # for this call override the default encoder
   response = client.execute_gql_query("workflows", QueryResponse, response_encoder=basemodel_encoder)
   print(response)
   # Response type is a list of BaseModels
   # [QueryResponse(workflowId=1, workflowName='gql3_full - workflow_name', workflowDescription='gql3_full - workflow_description'), QueryResponse(workflowId=2, workflowName='VBI base calibration', workflowDescription='The base set of calibration tasks for VBI.')]

Best Practices
--------------

**Simple Conversions between Camel Case and Snake Case**

If your target GQL endpoint uses camelCase, follow these steps.

First, create a ``CamelHelper`` class:

.. code:: python

  # limited to pydantic V2
  from pydantic import BaseModel
  from pydantic import ConfigDict
  from pydantic.alias_generators import to_camel


  class CamelHelper(BaseModel):
      """
      Helper Class.
      Extend this class as if it were BaseModel.
      Within the subclass, define the fields using snake_case.
      Upon BaseModel instantiation, either snake_case or camelCase is valid input.
      Normal model_dump will create a dict with snake_case keys.
      Alias model_dump, with `by_alias=True`, will create a dict with camelCase keys.
      """
      model_config = ConfigDict(
          alias_generator=to_camel,
          populate_by_name=True,
      )

When defining your models, extend ``CamelHelper``, instead of ``BaseModel``.
Define the attributes using snake_case.

.. code:: python

  class AliasSample(CamelHelper):
      required_str: str
      optional_float: float | None = None

  # camelCase accepted upon creation
  alias_sample = AliasSample(requiredStr="hello")


The internal key names will be snake_case.
You can dump to a ``dict`` with snake_case keys:

.. code:: python

  alias_data_snake: dict = alias_sample.model_dump()

Or you can dump to a ``dict`` with camelCase keys:

.. code:: python

  alias_data_camel: dict = alias_sample.model_dump(by_alias=True)

**Passing a dict as a dict**

To pass a ``dict`` as a ``dict``,
the GQL Server must define the data type of the corresponding field as ``JSON``.
Note that ``JSON`` and ``JSONString`` are not the same thing.
``JSONString`` expects a json encoded string (frequently via json.dumps) which is transformed via json.loads.
``JSON`` expects an object and no transformation occurs.

Define the field as a ``dict`` within the model:

.. code:: python

  # limited to pydantic V2
  from pydantic import BaseModel

  class SampleCreateRequest(CamelHelper):
      required_str:  str | None = "Awesome"
      payload: dict | None = None

  dummy_payload = {
      "key_str": "Party On, Wayne",
      "key_int": 42,
      "key_float": 3.141592,
      "key_none": None,
      "key_true": True,
      "key_false": False,
  }
  create_request = SampleCreateRequest(
      payload = dummy_payload
      )

Execute the request:

.. code:: python

  # sample response
  class SampleResponse(CamelHelper):
      payload: dict | None = None

  # url for a running GQL server
  client = GraphQLClient(gql_uri="http://localhost:8080/graphql")

  # assuming GQL server defines `payload` as `JSON`
  pseudo_response = client.execute_gql_mutation(
     mutation_base="sampleMutation",
     mutation_response_cls=SampleResponse,
     mutation_parameters=wrap_request(create_request)
  )

  assert isinstance(create_request.payload, dict)
  assert isinstance(pseudo_response.payload, dict)
  assert create_request.payload == pseudo_response.payload

.. |codecov| image:: https://codecov.io/bb/dkistdc/graphql_client/branch/master/graph/badge.svg
   :target: https://codecov.io/bb/dkistdc/graphql_client
