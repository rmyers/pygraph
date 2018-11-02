
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
import uvicorn

from graphql import build_schema, extend_schema, parse, graphql_sync

ROOT_QUERY = """
  type Query {
    _empty: String
  }
  enum CacheControlScope {
            PUBLIC
            PRIVATE
          }
  directive @cacheControl(
            maxAge: Int
            scope: CacheControlScope
          ) on FIELD_DEFINITION | OBJECT | INTERFACE
"""

EXTENDED = """
  type User {
    name: String
    last: String
  }

  extend type Query {
    hello(name: String): User
  }
"""

ACTIONS = """
  type ComputeServerAction {
    name: String!
    text: String!
    icon: String
    enabled: Bool
    tooltip: String
    form: ActionForm  # details to follow
    mutation: String  # mutation query
  }

  extend type Query {
    computeServerActions(): [ComputeServerAction]
  }
"""


class Action:
    text = 'Reboot Server'
    icon = 'reboot'
    @property
    def tooltip(self):
        if not self.enabled:
            return 'You do not have permission to do this!'


def computeServerActions(_source, info):
    actions = []
    for action in SERVER_ACTION_LIST:
        enabled = info.context.user.has_permission_to_do_action(action)
        actions.append(action(enabled=enabled))
    return actions


schema = build_schema(
  ROOT_QUERY
)
schema = extend_schema(schema, parse(EXTENDED))

query = """
{
  hello(name: "frank") {
    name
    last
  }
}
"""


class Resource:
    pass

class Filter:
    def __init__(self, filter_string: str):
        self.attribute, self.value = filter_string.split(':')
    def matches(self, server):
        return getattr(server, self.attibute, None) == self.value

async def computeServers(_source, info, region='ALL', filters=None):
    # If we were lucky there would be a query arg for the server list api
    # never fear we can do this logic here and make it performant with caching.
    servers = await info.context.ComputeServer.list(region)
    filter_list = [Filter(f) for f in filters.split(',')]
    return list(filter(filter_list.matches, servers))  # prolly doesn't work :)



class ComputeServer(Resource):
    catalog_type = 'compute'
    root = 'servers'

    async def flavor(self, info):
        # we use a list call because we memoize/cache the api calls
        flavors = await info.context.ComputeFlavor.list(self.region)
        for flavor in flavors:
            if flavor.id == self.flavor['id']:
                return flavor


class User:

    def __init__(self, name):
        self.name = name

    def last(self, info, **args):
        return "{'last': 'name'}"


def hello(source, info, name):
    return User(name)


registry = {
  'Query': {
    'hello': hello,
  },
  'User': {
    'laste': lambda _source, _info, **kwarg: 'frank'
  }
}


def resolver(resource, info, **kwargs):
    name = info.parent_type.name  # GQL schema type (ie Query, ComputeServer)
    try:
        # info.field_name is the attribute (ie name, id)
        res = registry[name][info.field_name]
    except KeyError:
        attr = getattr(resource, info.field_name, None)
        if attr:
            if callable(attr):
                return attr(info, **kwargs)
            return attr

    return res(resource, info, **kwargs)


results = graphql_sync(
    schema,
    query,
    field_resolver=resolver
)

print(results)


app = Starlette()
app.debug = True


@app.route('/home')
def homepage(request):
    return PlainTextResponse('text')


if __name__ == '__main__':
    print('done')
    assert uvicorn
    # uvicorn.run(app, http='h11', host='0.0.0.0', port=16000)
