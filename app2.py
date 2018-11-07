from graphql import build_schema, extend_schema, parse, graphql_sync

# This is the root query that we provide, since the Query type cannot be
# completely empty we need to provide something that we can extend with
# the schema you are extending.
ROOT_QUERY = """
  type Query {
    _empty: String
  }
"""

# This is an extended query which you would provide for a custom type.
# By extending the types you can spread the schema across multiple files
# for easier management. You can also have different endpoints only use
# a subset of your schema if you break it up.
EXTENDED = """
  type User {
    name: String
    last: String
    friend: User
  }
  extend type Query {
    hello(name: String): User
  }
"""

schema = build_schema(ROOT_QUERY)
extended_schema = extend_schema(schema, parse(EXTENDED))  # repeat as needed

sample_query = """{
  hello(name: "frank") {
    name
    last
  }
}
"""

class User:
    def __init__(self, name):
        self.name = name

def hello(source, info, name):
    return User(name)

# This is the registry
registry = {
  'Query': {
    'hello': hello,
  },
  'User': {
    'last': lambda _source, _info, **kwargs: 'smith'
  }
}

def resolver(resource, info, **kwargs):
    type_name = info.parent_type.name  # GQL schema type (ie Query, User)
    field_name = info.field_name  # The attribute being resolved (ie name, last)
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


results = graphql_sync(
    extended_schema,
    sample_query,
    field_resolver=resolver
)

print(results)
