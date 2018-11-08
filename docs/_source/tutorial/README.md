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

## Our First Schema


