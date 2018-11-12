import json

from django import http
from django.middleware.csrf import get_token
from django.shortcuts import render_to_response
from django.template import Context
from graphql import (
    extend_schema,
    parse,
    graphql,
    get_default_backend,
)

from resolver import legacy_middleware
from schema import schema

from resources.commit import calendar


registry = {
    "Query": {
        "getCommitCalendar": calendar.getCommitCalendar,
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


def middlewar(next, *args, **kwargs):
    # type: (Callable, *Any, **Any) -> Promise
    return resolver(*args, **kwargs)


def graph(request):
    if request.method == 'GET':
        # All graphql requests are POST, so if it is a GET we can just
        # render the graphql playground.
        ctx = Context({
            # Pass down the csrftoken to the playground so it can be set as
            # the X-CSRFToken header during requests.
            'csrftoken': get_token(request),
        })
        return render_to_response('playground.html', context_instance=ctx)

    elif request.method == 'POST':
        # Do the query and return results
        content_type = request.META.get('CONTENT_TYPE')
        if content_type == "application/graphql":
            print('app/gql')
            query = {"query": request.body.decode()}
        elif content_type == "application/json":
            print('app/json')
            query = json.loads(request.body.decode("utf-8"))
        else:
            return http.HttpResponseBadRequest()

        # execute the query against our schema and resolvers
        print(query)
        results = graphql(
            schema=schema,
            query=query,
            middleware=[legacy_middleware],
        )
        content = json.dumps(results.to_dict())
        print(content)
        return http.HttpResponse(content, content_type='application/json')

    raise http.HttpResponseNotAllowed()
