import json

from django import http
from django.middleware.csrf import get_token
from django.shortcuts import render_to_response
from django.template import Context
from graphql import get_default_backend

from resolver import resource_registry
from schema import schema


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
        document = backend.document_from_string(schema, query)
    except Exception:
        raise

    try:
        return document.execute(
            root=None,
            variables=variables,
            operation_name=operation_name,
            context=request,
        )
    except Exception:
        raise


for _type, resolvers in resource_registry.iteritems():
    type_obj = schema.get_type(_type)
    if type_obj is None:
        continue
    for field_name, resolve_func in resolvers.iteritems():
        field = type_obj.fields.get(field_name)
        if field is None:
            continue
        field.resolver = resolve_func
        field.description = resolve_func.__doc__


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
            data = {"query": request.body.decode()}
        elif content_type == "application/json":
            print('app/json')
            data = json.loads(request.body.decode("utf-8"))
        else:
            return http.HttpResponseBadRequest()

        # execute the query against our schema and resolvers
        query, variables, operation_name = get_graphql_params(request, data)
        results = execute_graphql_request(request, data, query, variables, operation_name)
        content = json.dumps(results.to_dict())
        print(content)
        return http.HttpResponse(content, content_type='application/json')

    raise http.HttpResponseNotAllowed()


def frontend(request):
    return render_to_response('frontend.html')
