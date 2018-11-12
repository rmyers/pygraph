import os

from graphql import build_ast_schema, extend_schema, parse
from graphql.type import (
    GraphQLArgument,
    GraphQLEnumType,
    GraphQLEnumValue,
    GraphQLField,
    GraphQLInterfaceType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLString,
)

# We need to have a root query that we can extend, according to th SDL spec
# we can not have an empty query type. So we initialize it with `_empty` which
# will never get used.
root_query = GraphQLObjectType(
    "Query",
    {"_empty": GraphQLField(GraphQLString)}
)

# In order to extend the schema we need to start with a valid schema
# class instance. In graphql-core-next we can use a SDL file for the root
# as well. Here we need a little hack to future proof the rest of our
# application structure.
root_schema = GraphQLSchema(
    query=root_query
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

schema_files = os.listdir(os.path.join(BASE_DIR, 'gql'))
schema_files.sort()

for filename in schema_files:
    with open(os.path.join(BASE_DIR, 'gql', filename)) as schema_file:
        schema_data = schema_file.read()
        # Each time we extend the root schema it makes a copy and returns
        # the newly extended schema and the orginal is unchanged.
        root_schema = extend_schema(root_schema, parse(schema_data))


# Just expose it as schema so we don't need to remember what we called it.
schema = root_schema
