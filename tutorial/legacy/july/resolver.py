
from resources.commit import calendar


resource_registry = {
    "Query": {
        "getCommitCalendar": calendar.getCommitCalendar,
    }
}


def resolver_func(resource, info, **kwargs):
    global resource_registry
    type_name = info.parent_type.name  # GQL schema type (ie Query, User)
    field_name = info.field_name  # The attribute being resolved (ie name, last)
    print('IN RESOLVER')
    print(type_name)
    print(field_name)
    print(resource)
    print(info)
    print('END RESOLVER')
    try:
        # First check if there is a customer resolver in the resource_registry
        # (ie Query:hello, User:last)
        custom_resolver = resource_registry[type_name][field_name]
        return custom_resolver(resource, info, **kwargs)
    except KeyError:
        # If there is not a custom resolver check the resource for attributes
        # that match the field_name. The resource argument will be the result
        # of the Query type resolution. In our example that is the result of
        # the `hello` function which is an instance of the User class.
        return getattr(resource, field_name, None)


def legacy_middleware(next, *args, **kwargs):
    # We need to handle the old interface to graphql resolution. In the
    # graphql-core-next version we can directly specify the resolver function.
    try:
        p = next(*args, **kwargs)
        print('I got here')
        return p.then(resolver_func(*args, **kwargs))
    except Exception:
        print('RESOLVER Exception!')
        return resolver_func(*args, **kwargs)
    # r = resolver_func(*args, **kwargs)
    # if r is not None:
    #     return r
    # return next(*args, **kwargs)
