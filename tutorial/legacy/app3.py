import json

from graphql import (
    extend_schema,
    parse,
    build_ast_schema,
    graphql,
    get_default_backend,
)
from graphql.type import (
    GraphQLField,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLString,
)
from graphql.utils.schema_printer import print_schema

ROOT_QUERY = """
type Query {
  # An empty query so we can extend it later
  _empty: String
}

schema {
  query: Query
}
"""

# This is an extended query which you would provide for a custom type.
# By extending the types you can spread the schema across multiple files
# for easier management. You can also have different endpoints only use
# a subset of your schema if you break it up.
EXTENDED = """
type Commit {
    hash: String!
    message: String
    author: String
    timestamp: String
}
type CommitCalendar {
    start: String!
    end: String!
    commits: [Commit]
}

extend type Query {
    getCommitCalendar(username: String): CommitCalendar
}
"""

root_query = GraphQLObjectType(
    "Query",
    {"_empty": GraphQLField(GraphQLString)}
)

root_schema = GraphQLSchema(
    query=root_query
)


extenders = extend_schema(root_schema, parse(EXTENDED))

extended_schema = build_ast_schema(parse(print_schema(extenders)))  # repeat as needed

print(dir(extended_schema))
print(extended_schema.get_type_map())

print(dir(extended_schema.get_type('Query')))
query = extended_schema.get_type('Query')
for field, obj in query.fields.items():
    print(obj.resolver)
    print(dir(obj))

sample_query = """{
  getCommitCalendar(username: "frank") {
    start
    end
  }
}
"""

class User:
    def __init__(self, name):
        self.name = name

from july.resources.commit import calendar

def hello(source, info, username):
    return calendar.CommitCalendar(username)

# This is the registry
registry = {
  'Query': {
    'getCommitCalendar': hello,
  }
}

# wrap our registered thingy
for _type, resolvers in registry.iteritems():
    type_obj = extended_schema.get_type(_type)
    if type_obj is None:
        continue
    for field_name, resolve_func in resolvers.iteritems():
        field = type_obj.fields.get(field_name)
        if field is None:
            continue
        field.resolver = resolve_func


def resolver(resource, info, *args, **kwargs):
    type_name = info.parent_type.name  # GQL schema type (ie Query, User)
    field_name = info.field_name  # The attribute being resolved (ie name, last)
    # print('IN RESOLVER')
    # print(type_name)
    # print(field_name)
    # print(resource)
    # print(info)
    # print('END RESOLVER')
    try:
        # First check if there is a customer resolver in the registry
        # (ie Query:hello, User:last)
        custom_resolver = registry[type_name][field_name]
        return custom_resolver(resource, info, **kwargs)
    except KeyError:
        # If there is not a custom resolver check the resource for attributes
        # that match the field_name. The resource argument will be the result
        # of the Query type resolution. In our example that is the result of
        # the `hello` function which is an instance of the User class.
        return getattr(resource, field_name, None)


def reversed_middleware(next, *args, **kwargs):
    # type: (Callable, *Any, **Any) -> Promise
    # r = resolver(*args, **kwargs)
    # if r is not None:
    #     return r
    # return next(*args, **kwargs)
    p = next(*args, **kwargs)
    # print(dir(p))
    return p.then(resolver(*args, **kwargs))


def get_graphql_params(request, data):
    query = request.GET.get("query") or data.get("query")
    variables = request.GET.get("variables") or data.get("variables")

    operation_name = request.GET.get("operationName") or data.get("operationName")
    if operation_name == "null":
        operation_name = None

    return query, variables, operation_name


def execute_graphql_request(request, data, query, variables, operation_name):
    backend = get_default_backend()
    try:
        document = backend.document_from_string(extended_schema, query)
    except Exception:
        raise

    try:
        return document.execute(
            root=None,
            variables=variables,
            operation_name=operation_name,
            context=request,
            # middleware=[reversed_middleware]
        )
    except Exception:
        raise


class FakeRequest:
    GET = {}
    session = {}


def doo_it():
    request = FakeRequest()
    data = {u'query': u'{getCommitCalendar(username: "rmyers") { start end commits { hash }}}', u'variables': {}, u'operationName': None}
    query, variables, operation_name = get_graphql_params(request, data)
    return execute_graphql_request(request, data, query, variables, operation_name)


results = doo_it()

print(dir(results))
print(results.data)
print(results.errors)
print(json.dumps(results.to_dict()))
