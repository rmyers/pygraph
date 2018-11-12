# Pygraph Tutorial

Everyone likes examples. In this tutorial we will go through a real world
example of converting an existing Django web site to one using pygraph.
Green field tutorials always look great on paper. But how often do you
ever get a chance to do that? If you are like me you have to work within the
system you have in order to make any changes. No manager is willing to let
you code for 6 months while change requests pile up for your existing site.

We are going to take a pragmatic approach to introducing graphql in your
application. With a little bit of work you can hopefully introduce this into
your environment and no one will even notice. Except you will be happy again
because your site will be easier to reason about. Your logic will live on
the server again and you will no longer be slave to NPM and caring about
things like what browsers support various ES6 rules.

Even if you *do* like Javascript, you will appreciate it becoming easier to
maintain. We hope you will learn something and will get more things done
faster with less headaches.

## Re-engineering Effort

(Shameless plug) [Julython](http://julython.org) is a community that gets
together in july to work on opensource projects. It has not received a lot on
attention in the past few years (volunteer time is hard to prioritize). The
site it self is pretty simple but it does interact with the github api and uses
websockets to show progress in real time.

While the site is dormant for 11 months of the year, we can still pretend that
it is under heavy usage and we will introduce our changes incrementally so
we do not have any down time. We need to increase our engagement and provide
a new framework to build on.

Hopefully we can leave the site better than when it started.

## Lay of the Land

First lets have a look at the current state of affairs. Here are the current
list of dependencies and versions we have to work with. It is not pretty and
it is fairly out of date. Attempting to update any single piece of this puzzle
is hard because we haven't been keeping up with these libraries. Since we
have a ton of dependencies that depend on others.

* Server
  * Nginx 1.5
  * Nginx push stream module (websockets) 1.4
  * Ubuntu 14.04
  * gunicorn 1.4
  * Python 2.7.11
* Python Application
  * Django==1.6.1
  * django-tastypie==0.9.15
  * Fabric==1.5.1
  * django-social-auth==0.7.28
  * iso8601==0.1.4
  * django-debug-toolbar==1.3
  * requests
  * South
  * mock
  * jsonfield>=0.9.20
  * pytz
  * pep8
  * markdown
* Client Side
  * backbone.js
  * d3-3.2.0.js
  * jquery-1.7.2.js
  * jquery.timeago-1.3.0.js
  * knockback-0.16.7.js
  * knockout-2.2.0.js
  * pushstream.js
  * underscore-1.4.1.js

So I'm not going to bore you with the nitty gritty details... but I'll update
all the things I can and then report back. You should do the same with your
site, be sure to update your dependencies (I'll wait)

All done? good that was easy j/k

For pygraph to work and the smoothest transition you should be on at least
Python 3.6. That might not be as easy as it sounds. So I'm willing to let
you punt and bring this up as a different service if you need to. Micro-services
for the win! Whether you wish to keep a monolithic application or not is out
of the scope of this tutorial.

I am unable to update to python 3.6 at this time. So we are going to have to
get creative. We can still use graphql but we can't use pygraph 'just yet'.
Since everyone should be using graphql (cause it is the bees knees) I'm first
going to build with the tools I have. Then once we have refactored out a few
things we can safely update our site to use 3.6+ and drop all the old
dependencies.

## Where to Begin? The Hard Way

Okay so we can't use pygraph yet, do you need pygraph at all? How can we do
this without a fancy framework.

I randomly selected the leader board page as a starting page. It is a page
that lists the top 20 people, teams and locations for the current game.

Here is the schema for the existing database tables:

```sql
CREATE TABLE "people_commit" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer REFERENCES "july_user" ("id"),
    "hash" varchar(255) NOT NULL UNIQUE,
    "author" varchar(255) NOT NULL,
    "name" varchar(255) NOT NULL,
    "email" varchar(255) NOT NULL,
    "message" varchar(2024) NOT NULL,
    "url" varchar(512) NOT NULL,
    "project_id" integer,
    "timestamp" datetime NOT NULL,
    "created_on" datetime NOT NULL,
    "files" text
)
;
CREATE TABLE "people_project" (
    "id" integer NOT NULL PRIMARY KEY,
    "url" varchar(255) NOT NULL,
    "description" text NOT NULL,
    "name" varchar(255) NOT NULL,
    "forked" bool NOT NULL,
    "forks" integer NOT NULL,
    "watchers" integer NOT NULL,
    "parent_url" varchar(255) NOT NULL,
    "created_on" datetime NOT NULL,
    "updated_on" datetime NOT NULL,
    "slug" varchar(50) NOT NULL,
    "service" varchar(30) NOT NULL,
    "repo_id" integer,
    "active" bool NOT NULL
)
;
CREATE TABLE "people_location" (
    "slug" varchar(50) NOT NULL PRIMARY KEY,
    "name" varchar(64) NOT NULL,
    "total" integer NOT NULL,
    "approved" bool NOT NULL
)
;
CREATE TABLE "people_team" (
    "slug" varchar(50) NOT NULL PRIMARY KEY,
    "name" varchar(64) NOT NULL,
    "total" integer NOT NULL,
    "approved" bool NOT NULL
)
;
CREATE TABLE "people_language" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(64) NOT NULL
)
;
CREATE TABLE "people_userbadge" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "july_user" ("id"),
    "badges" text
)
;
CREATE TABLE "game_game" (
    "id" integer NOT NULL PRIMARY KEY,
    "start" datetime NOT NULL,
    "end" datetime NOT NULL,
    "commit_points" integer NOT NULL,
    "project_points" integer NOT NULL,
    "problem_points" integer NOT NULL
)
;
CREATE TABLE "game_player_boards" (
    "id" integer NOT NULL PRIMARY KEY,
    "player_id" integer NOT NULL,
    "board_id" integer NOT NULL,
    UNIQUE ("player_id", "board_id")
)
;
CREATE TABLE "game_player" (
    "id" integer NOT NULL PRIMARY KEY,
    "game_id" integer NOT NULL REFERENCES "game_game" ("id"),
    "user_id" integer NOT NULL REFERENCES "july_user" ("id"),
    "points" integer NOT NULL
)
;
CREATE TABLE "game_board" (
    "id" integer NOT NULL PRIMARY KEY,
    "game_id" integer NOT NULL REFERENCES "game_game" ("id"),
    "points" integer NOT NULL,
    "project_id" integer NOT NULL REFERENCES "people_project" ("id")
)
;
CREATE TABLE "game_languageboard" (
    "id" integer NOT NULL PRIMARY KEY,
    "game_id" integer NOT NULL REFERENCES "game_game" ("id"),
    "points" integer NOT NULL,
    "language_id" integer NOT NULL REFERENCES "people_language" ("id")
)
;
CREATE TABLE "july_user_projects" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "project_id" integer NOT NULL REFERENCES "people_project" ("id"),
    UNIQUE ("user_id", "project_id")
)
;
CREATE TABLE "july_user_groups" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id"),
    UNIQUE ("user_id", "group_id")
)
;
CREATE TABLE "july_user_user_permissions" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id"),
    UNIQUE ("user_id", "permission_id")
)
;
```

Or at least that is most of the schema, you don't need to read it closely but
we will use that as a guide for our graphql types.

## Installation

First we need to get the graphql core library installed, as this is the only
prereq that we have:

```bash
$ pip install graphql-core
```

Once you have that installed we can start adding this to our Django views.

## First Query to Migrate

So we have a large application and it is not entirely clear where to start.
One thing I suggest is to see where you are using non-standard api calls or
api calls that combine multiple resources.

There are a few candidates for our demo site, I randomly choose to migrate the
commit calendar code to using graphql. First lets look at the existing code.

Currently the commit calendar is a custom query that counts the commits for
each day and returns start, end, and list of commit objects:

```python
    @classmethod
    def calendar(cls, game, **kwargs):
        """
        Returns number of commits per day for a date range.
        """
        count = cls.objects.filter(
            timestamp__range=(game.start, game.end), **kwargs) \
            .extra(select={'timestamp': 'date(timestamp)'}) \
            .values('timestamp').annotate(commit_count=Count('id'))
        resp = {
            'start': game.start.date(),
            'end': game.end.date(),
            'objects': list(count)
        }
        return resp
```

That is exposed as a non-standard api endpoint (the application is using
tastypie for api now) it looks like this:

```python
class CommitResource(CORSResource):
    user = fields.ForeignKey(UserResource, 'user', blank=True, null=True)
    project = fields.ForeignKey(ProjectResource, 'project',
                                blank=True, null=True)

    class Meta:
        queryset = Commit.objects.all().select_related(
            'user', 'project')
        cache = SimpleCache(timeout=30)
        allowed_methods = ['get']
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'project': ALL_WITH_RELATIONS,
            'timestamp': ['exact', 'range', 'gt', 'lt'],
        }

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/calendar%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_calendar'),
                name="api_get_calendar"),
        ]

    def get_calendar(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.throttle_check(request)
        filters = {}

        game = Game.active_or_latest()
        username = request.GET.get('username')
        if username:
            filters['user__username'] = username

        # user = kwargs.get('user', None)
        calendar = Commit.calendar(game=game, **filters)
        return self.create_response(request, calendar)
```

And for completeness here is the SQL for the commit table:

```sql
CREATE TABLE "people_commit" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer REFERENCES "july_user" ("id"),
    "hash" varchar(255) NOT NULL UNIQUE,
    "author" varchar(255) NOT NULL,
    "name" varchar(255) NOT NULL,
    "email" varchar(255) NOT NULL,
    "message" varchar(2024) NOT NULL,
    "url" varchar(512) NOT NULL,
    "project_id" integer,
    "timestamp" datetime NOT NULL,
    "created_on" datetime NOT NULL,
    "files" text
)
```

### Write the Schema

First we will need to create a schema for Commit and Calendar so that we can
accurately model what is going on. The original code and api sort of glosses
over the fact that these are actually two different resources. It is the
same database but it is a different view of the data :shrug:! We shall fix
that now that we are refactoring things.

Here is the `CommitCalendar` type:

```graphql
type CommitCalendar {
    start: String!
    end: String!
    commits: [Commit]
}
```

And of course we then need a `Commit` type (for now just include the minimum):

```graphql
type Commit {
    hash: String!
    message: String
    author: String
    timestamp: String
}
```

And for the commit calendar we just need to expose a query to fetch it:

```graphql
extend type Query {
    getCommitCalendar(username: String) CommitCalendar
}
```

**NOTE:** We use camelcase here because this is meant to be used by Javascript
          and this help signify that.

### Organization for Those Who Like That Sort of Thing

Where should we put all this stuff? It is really up to you how you want to
organize your application. But I find it is best when you organize your SDL
files by type, that is one major type per graphql file.

Since this is a django project, I'll just create a new 'application':

```bash
$ python manage.py startapp graph
```

We can have circular references in the SDL but if you extend any types those
will need to be extended in order. So we'll just make sure we have a system
that can handle this. The name of the files don't actually matter so I'm going
to suggest that you name them like `001_commit.graphql`. Then if you need
to order them you can just increment the prefix accordingly. So now we have
this structure:

```gql
july/
    /graph
    /graph/gql/001_commit.graphql
    /graph/gql/002_commit_calendar.graphql
    /graph/schema.py
    /graph/resolvers/commit/commit.py
    /graph/resolvers/commit/calendar.py
```

**NOTE:** If you are concerned about discovering your schema, don't because the
          graphql playground does this very well as we will see later.

Okay so to get the schema files in we need to walk the folder and extend the
base schema. Here is what our schema file will look like:

```python
import os

from graphql import build_schema, extend_schema, parse, graphql

ROOT_QUERY = """
  type Query {
    _empty: String
  }
"""

root_schema = build_schema(ROOT_QUERY)

schema_files = os.listdir('gql')
schema_files.sort()

for filename in schema_files:
    with open(os.path.join('gql', filename)) as schema_file:
        schema_data = schema_file.read()
        root_schema = extend_schema(root_schema, parse(schema_data))


# Just expose it as schema so we don't need to remember what we called it.
schema = root_schema
```

Which will parse all the files and extend the root schema. Now all we need
is a base resolver function will will resolve all our custom resolvers and
classes. Oh wait first we need to create those.

### Resolvers

A resolver is pretty simple it just has to adhere to the following spec:

`def resolver(resource: Any, info: Any, *args, **kwargs)`

* `resource`: Is the resource that was resolved, or None.
* `info`: Is the shared context and the parser info.
* `args`: Optional positional args that are passed to the Query or Mutation.
* `kwargs`: Optional keyword args that are passed to the Query or Mutation.

What we hope to acheive at the end of the day is a way to join our schema to
reality. We do that in pygraph with decorators which make it easy for you to
connect the pieces together. That is the glue that binds the disjoined world.
While it is not always easy to see the big picture I hope that you are able to
follow along and learn something.

This tutorial is attempting to show you how it could be done without the
framework. Then we will refactor the code base to use pygraph. To see how it
can help you to organize your code and make it sing.

Then to wrap it up we will sprinkle in a little web components action and you
will be able to program on the web again. And you wont have to learn too much
Javascript. And your code will live on the server again! Happy and caged safe
from prying eyes and 'clients'.

Django ORM is good for pulling out the pieces that we need. I was temped at
first to pull down some raw sql but it is close to what we need. So for the
commit calendar we can just use the existing method and tie that to the
schema. Pretty cool. But how?

Well, all we need to do is to provider our own custom resolver to the excution
of the Query or Mutation. Then as the graph is resolved it will call our
function to 'resolve' things duh!

Here is our `resolver` function:

```python
registry = {}

def resolver(resource, info, **kwargs):
    global registry
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
```

So now we just need to get things into that registry. The registry should be
a set of factory functions or classes that have a `__call__` method. In
pygraph you would use our decorators but here you can simply import the
things you need and fill in the registry by hand.

By manually populating this registry you also make it much easier to see where
everything is defined. Like this:

```python
from resolvers.commit import calendar

registry = {
    'Query': {
        'getCommitCalendar': calendar.CommitCalendar,
    }
}
```

And that looks a little like this:

```python

from july.people.models import Commit
from july.game.models import Game

class CommitCalendar:
    # start: datetime
    # end: datetime
    # commits: [Commit]

    def __init__(self, username=None):
        # TODO: check info.context for the correct user permissions?
        self.game = Game.active_or_latest()
        self.filters = {}
        if username is not None:
            self.filters['user__username'] = username

        self.start = game.start
        self.end = game.end

    @property
    def commits(self):
        # None -> [Commit]
        # Allow for lazy loading
        calendar = Commit.calendar(game=game, **filters)
        return calendar['objects']


def getCommitCalendar(source, info, username=None):
    return CommitCalendar(username=username)
```

We might choose to just add some functions in the `july.people.models` module
which might make sense as this is but here I'm trying to make it nice and
easy to find all the resolvers.

What happens when you execute the Query"

```gql
query getCommitCalendar(username: $username) {
    start
    end
    commits
}
```

1. The middleware classes are called and we return our resolver function.
1. The `resolver` function is called and the `info.parent_type.name = 'Query'`
2. The `info.field_name` is set to `getCommitCalendar`
3. We look up in the registry for `registry['Query']['getCommitCalender']`
4. We return the results of the call `getCommitCalender(resource, info, **kwargs)`
5. We get back an instance of the CommitCalendar class.
6. The resolver is then called again for each of the three `start`, `end`, `commits`
7. For each call the `resource` argument is set to the CommitCalendar
8. For each call the `info.parent_type.name = 'CommitCalendar'`
9. And each call the `info.field_name` is either `start`, `end`, or `commits` but they are called in order
10. Our resolver looks in the registry for `registry['CommitCalendar'][info.field_name]`
11. If we find a custom resolver in the registry we return that call just like `resolver(resource, info, **kwargs)`
12. If there is no custom resolver we fall back to attribute lookups on the `resource` which is the CommitCalendar instance.

As long as all the types match then are results are returned. If there is any
errors in the processing we will return a None or a null in Javascript for that
field.

So now all we need to do is connect this to a view and we can start testing it
out. Since by default all the queries are synchronous there is no reason not
to return it in a normal Django view. In the future we will refactor this to
use the new python async loop. But for now we will just create a simple
view and response.

### Wire this Baby Up

We just need to connect the dots and serve the newly generated schema. To do
that all we need is a new view and url which is easy enough. We'll add a route
to our main `urls.py` like:

`url(r'^api/v2/graphql$', 'july.graph.views.graph', name='graph'),`

Now our `graph` view looks like this:

```python
import json
from django.shortcuts import render_to_response
import graphql

from resolver import resolver
from schema import schema


def graph(request):
    if request.method == 'GET':
        # All graphql requests are POST, so if it is a GET we can just
        # render the graphql playground.
        return render_to_response('graph/playground.html')
    elif request.method == 'POST':
        # Do the query and return results
        content_type = request.META.get('CONTENT_TYPE')
        if content_type == "application/graphql":
            query = {"query": request.body.decode()}
        elif content_type == "application/json":
            query = json.loads(request.body.decode("utf-8"))
        else:
            raise Exception('bad content type')

        # execute the query against our schema and resolvers
        results = excute()

```

