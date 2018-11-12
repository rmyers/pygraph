import json

from graphql import (
    extend_schema,
    parse,
    graphql,
    get_default_backend,
)
from graphql.type import (
    GraphQLField,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLString,
)

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

extended_schema = extend_schema(root_schema, parse(EXTENDED))  # repeat as needed

print(dir(extended_schema))

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
  },
  'User': {
    'last': lambda _source, _info, **kwargs: 'smith'
  }
}

def resolver(resource, info, *args, **kwargs):
    type_name = info.parent_type.name  # GQL schema type (ie Query, User)
    field_name = info.field_name  # The attribute being resolved (ie name, last)
    print(info.operation.directives)
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
    return resolver(*args, **kwargs)


backend = get_default_backend()

results = graphql(
    extended_schema,
    {u'query': u'{getCommitCalendar(username: "rmyers") { start end }}', u'variables': {}, u'operationName': None}['query'],
    middleware=[reversed_middleware],
)

print(dir(results))
print(results.data)
print(results.errors)
print(json.dumps(results.to_dict()))
