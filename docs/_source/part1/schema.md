# Schema Design

All GraphQL adventures start with the schema file you should be very familiar
with it if you wish to be successful. First things first, you may be tempted
to use a tool like [Graphene](https://graphene-python.org) to model your
schema. While this is 'ok' you are going to be locked into a single
implementation for your site. Maybe you are fine with this, I strongly encourage
you to give the DSL a try. Some of the benefits you will get is the ability to
store the schema files separate from your code in files named like
`my_schema.graphql`.

This offers your code editor to syntax highlight the files as well as allowing
you to reuse the schema with other tools. Flexibility is key, and avoiding
vendor lock-in is a win. If you decide that pygraph is not for you, there is
less work to move to a different server or language entirely.

The only drawback to using the shema files is that we need to manually wire
up the resolvers to the schema. It is not hard, it is just tedious, which is
where pygraph will help you out. With pygraph you just have to use our
decorator on your resolver class or function like:

```python
@register.query
async def getPerson(_source, info, argA, argB):
    return 'something cool'


@register.resource
class Person(BaseAPIResource):
    base_url = '/api/v1/person'

    @property
    async def computed_value(self, source, info):
        return 'something else'
```

There is nothing magical about our decorator, and how we join them. We use
the [graphql-core-next](https://graphql-core-next.readthedocs.io/en/latest/) to
parse the GQL schema and use a custom resolver to map resolvers to the schema.
Here is a full working example of the process:

```python
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
    # A custom resolver for fields that are not on our model
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
```

If you copy that into a file and run it like `python myquery.py` you will see:

```
ExecutionResult(data={'hello': {'name': 'frank', 'last': 'smith'}}, errors=None)
```

Good schema designs should include only the information you know you are going
to use. It is easy to add new fields yet it is usually hard to deprecate old
ones.

## Scalar Types

There are 5 main Scalar types that are provided by the GQL language. Those are

 * _Int_: Signed 32‐bit integer
 * _Float_: Signed double-precision floating-point value
 * _String_: UTF‐8 characters
 * _Boolean_: true/false
 * _ID_: A unique identifier, which is serialized to String

These map to the Javascript types so they can serialize to JSON. A field can
be either a single value or a list of types. Circular references are possible
in the GQL language as well. And ordering does not matter, except if you are
extending an existing type, they need to be defined before you extend them.

## Object Types

You can extend the type system with your own custom object types. You have seen
some of this already here is a refresher:

```graphql
type User {
  id: ID!
  first: String
  last: String
  email: String
  bestFriend: User  # Circular Reference!
}
```

You can extend a type like to provide extra capabilities, this could be used
to dynamically extend a type depending on the request user. Or you could
extend all your types on a special admin only interface:

```graphql
extend type User {
  specialField: String
}

extend type Query {
  getUserBySpecialField(special: String): User
}
```

How you organize it is up to you, and it may take a bit of trial and error
as you design your schema. By using the GQL schema you have the flexibility to
choose how you want to expose your data in a easy to read format.

## Query Type

This is a special type which maps to the GET http verb of a typical REST api.
You can expose queries to return your custom object types. For example:

```gql
type Query {
  getUsers() [User]
  getGroups() [Group]
}
```

* _getUsers()_: Will return a list of User object types.
* _getGroups()_: Will return a list of Group object types.

## Mutation Type

Another special type is the Mutation which maps to POST/PUT/PATCH/DELETE verbs
of a REST api. You define these similarly to the query type to expose all the
possible actions you can take in your system.

```gql
type Mutation {
  createUser(name: String!, email: String!, birthday: String): User
  createGroup(name: String!): Group
}
```

* _createUser_: Has two required arguments and one optional one, and returns
                new User object type that was created.
* _createGroup_: Has only one required argument, and returns a new Group object type.

When you execute a mutation query you also can specify the fields to return just
like the Query type:

```gql
mutation {
  createUser(name: "Frank", email: "frank@bean.co", birthday: "monday") {
    name
    email
  }
}
```

Which will return the following response:

```json
{
  "data": {
    "createUser": {
      "name": "frank",
      "email": "frank@bean.co"
    }
  }
}
```

You can use these fields to update your cache on the client side. Or just
display the new object for the user.

## Enum Type

You can define enums as a special type like:

```gql
enum Permissions {
  ADMIN
  CREATE
  DELETE
  UPDATE
}
```

Enums are particularly useful for when the user has only a few options to
choose from. Also during development the GraphQL playground is able to
auto-complete these fields for you.

## Custom Directives

You can create custom directives which transform the data or markup the field
for the resolvers to use. For example here is a custom directive for
cacheControl:

```gql
  enum CacheControlScope {
    PUBLIC
    PRIVATE
  }
  directive @cacheControl(
    maxAge: Int
    scope: CacheControlScope
  ) on FIELD_DEFINITION | OBJECT | INTERFACE
```

This directive is to control the cache rules for a given object, field, or
interface. This is built into pygraph which was inspired by one provided by
[apollo-server](link to apollo). Depending on what fields you include in your
query will adjust the maxAge of the cache for this object. As an example here
is our User object type with cacheControl directives:

```gql
type User @cacheControl(maxAge: 1800) {
  id: ID!
  first: String
  last: String
  email: String
  bestFriend: User @cacheControl(maxAge: 60)
}
```

In this example you can see that the default max age for the User object will
be 1800 seconds. However if your query includes the `bestFriend` field the max
age will be reduced to 60 seconds for that reponse object. This way you can
optimize certain pages such as a quick list view to cache those responses for
longer since the fields needed are fewer and update less frequently. Then on
the full details page you would include more fields, and quite possibly
fields that update more frequently so you can reduce the max age for the
cached response.


