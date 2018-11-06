# TAKE BACK THE WEB

Using GraphQL and Python to move your business logic out of the hands of your
Javascript UI Clients and back to the server where they belong!

We have all been there at one point, not many people can say they have been
at a place for a number of years and only work on a system that never needs
updates. In the frantic world of the modern web things move quickly and the
tech that was hot last year is most likely not again. But so how do we continue
to progress forward without a tremendous amount of work? If your site is anything
like mine you didn't write it and it is probably not you first choice of
tech. But you are at a total loss as to how to replicate the functionality
in a new site for a project with 8 years of designs and 100's? of contributors.

What if there was a better way that way is GraphQL (I'll explain more in detail
later)

With GraphQL you can query from multiple sources all with a well defined schema
that not only gives you exactly the data you want but it gives it back to you
in the same structure. Think about that for a minute (find clever thing here)

People usually talk about the query part of GraphQL but the real power is the
ability to have custom resolvers to return that data. So while in a REST only
world you are constrained by the api team adding fields and properties in the
results. You now have the power to intercept all your api calls and transforms
them as you see fit. That could mean something as 'simple' as automatically
translating all the strings into a different language. Or checking a users
permissions and showing them only the options they are allowed to even preform
while not having to talk to a different team (cause code is better at communicating
with people than people are able to talk to each other think about that for
a minute or two)

## NOSQL vs SQL?

Let's explore what I mean when I say REST is like NOSQL and GraphQL is like
a SQL database. First a simple example lets say you have a NOSQL DB and you
have related data you need to have. Typically what is done in this scenario
is a term de-normalization which is the opposite of normalization. Say you
have a NOSQL DB and you want to model a person object:

```json
{
  "id": "1",
  "name": "frank",
  "email": "frank@tld.com"
}
```

This is a pretty simple object and the resulting queries will be fast which
is why you choose NOSQL in the first place. You didn't want to have to mess
with creating a schema for this straight forward model why waste time doing
boring stuff!

Then your manager comes over and says frank needs some friends which are also
person objects. Since there are no relations in a NOSQL database the easiest
thing to do is to de-normalize the data for the friends. Basically embed all
the details of your friends inside your object (which is easy to do since there
is no schema YAY!):

```json
{
  "id": "1",
  "name": "frank",
  "email": "frank@tld.com",
  "friends": [
    {
      "id": "2",
      "name": "jane",
      "email": "jane@tld.com"
    },
    {
      "id": "3",
      "name": "john",
      "email": "john@tld.com"
    }
  ]
}
```

Now every request to your NOSQL database includes this extra info, not to
mention you need to handle all the updates when a person updates the email
address.

What if I only need to get Frank's email address and I don't want all that
extra info? What if I need the friends list, but I need their friends as well?
Should we de-normalize the data even more? When do you stop?

Now maybe there are better way to NOSQL to solve this issue, they
are most likely hacks or you would need a masters degree in your database to
to explain it to someone else.

So now how does this look in SQL? Simple First we need to generate a schema
for a person and create a friends table to map them.

```SQL
CREATE TABLE IF NOT EXISTS person (
    id INT AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS friends
(
  person_id INT,
  friend_id INT,
  CONSTRAINT friends_pk PRIMARY KEY (person_id, friend_id),
  CONSTRAINT FK_person
      FOREIGN KEY (person_id) REFERENCES person (person_id),
  CONSTRAINT FK_friend
      FOREIGN KEY (friend_id) REFERENCES person (friend_id)
);
```

Now this is a huge amount of setup and you may need to know what you are
doing or use a fancy ORM like Django's to manage these tables yourself.

Query for all the person's:

```sql
SELECT * FROM person;
1           frank       frank@tld.com
2           jane        jane@tld.com
3           john        john@tld.com
```

I want the user details and all the friends name?

```sql
SELECT p.name, p.email FROM person p
  LEFT JOIN friends f on p.id = f.friend_id
  WHERE f.person_id = 1;
jane        jane@tld.com
john        john@tld.com
```

Now this is undoubtibly more work and more complicated to write. But it has
the nice benefit of only returning the data I want and it is fast as the
database can use indexes to resolve the data. The person table is the source
of truth for all things about the person and the friends table maps a
relation between them.

Also all your developers who have a little bit of SQL knowledge can easily
discover the relations themselves simply by asking the database what they are:

```sql
SHOW CREATE TABLE;
CREATE TABLE person (
    id INT AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
);
CREATE TABLE friends
(
  person_id INT,
  friend_id INT,
  CONSTRAINT friends_pk PRIMARY KEY (person_id, friend_id),
  CONSTRAINT FK_person
      FOREIGN KEY (person_id) REFERENCES person (person_id),
  CONSTRAINT FK_friend
      FOREIGN KEY (friend_id) REFERENCES person (friend_id)
);
```

Now I can make adhoc queries all day long until I get just the right mix of
data to performance. There are plenty of tools to help you in this journey
as well simply for the fact that your data is well defined, just like the
computer likes it to be!

## REST vs Graphql

So what does this have to do with graphql? Lets create a simple REST api for
our person table. *I'll just assume you chose SQL because you are smart
and a sensible reader!*

```python
class PersonAPI:
  def get(self, person_id):
    results = db.cursor.exec(PERSON_QUERY, person_id)  # you get the idea
    return person_to_json(results)
```

And we wire this up to the framework of our choice and start using it:

```json
Request:
GET /api/v1/person

Response:
{
  "id": "1",
  "name": "frank",
  "email": "frank@tld.com"
}
```

Now our person api maps directly to a single db query and everyone is happy
simple easy to read and we are done. Not so fast says your manager, she wants
you to add in the friends details too. Should we just provide links and make
the UI fetch those as well?

```json
Request:
GET /api/v1/person

Response:
{
  "id": "1",
  "name": "frank",
  "email": "frank@tld.com",
  "friends": [
    "/api/v1/person/2",
    "/api/v1/person/3"
  ]
}
```

It might work, and this is truly the *most* RESTful? way to do this. Ideally
in the REST world there is one url/uri for everything and all HTTP verbs are
used to manipulate them. Well, the world is not prefect and you will never
win an award for your website/api being technically correct in everyway.
You can only hope to keep your users happy with fancy new features.

In order to not be that person, you need to be flexible. We can reduce the
number of api calls we need to make simply by populating the data. Something
like:

```json
{
  "id": "1",
  "name": "frank",
  "email": "frank@tld.com",
  "friends": [
    {
      "id": "2",
      "name": "jane",
      "email": "jane@tld.com"
    },
    {
      "id": "3",
      "name": "john",
      "email": "john@tld.com"
    }
  ]
}
```

*Hmm, this is starting to look familiar...*

But now every rest call is returning all that extra friend info even when
you don't use any of it. Well you could easily add a query param to trigger
when to add info or which to add maybe something like:

```json
GET /api/v1/person/1?include=friends,and,other,fields
```

While that works it is not obvious and can easily be missed in your documentation
for your person endpoint. (You do document your apis correct?) The person who
comes after you might not appriciate that. It is also hard to 'discover' this
as it follows no real convention each endpoint may or may not honor this type
of query args. Not to mention *YOU* might not even be able to change the api
in this way, if this api is from a 3rd party.

What did we learn so far?

YOUR DATA HAS RELATIONS! It is not discrete pieces of information that does
not interact with anything.

You might see a correlation with other articles claiming that you shouldn't
be using an ORM to map to your SQL tables because of impedance mismatch.
(insert link here)

We need a protocol that takes these relations into account. This is where
GraphQL comes in. GraphQL was developed by Facebook and released in 2015 to
handle this problem in a more natural way. Sort of like sql maps really
well to most of your use cases. It goes one step further though as it is not
strictly tied to a single data source. It is agnostic to where or how you
get your data, yet it still provides a uniform schema to query it.

Lets start with our simple person type:

```gql
type Person {
  id Integer!  # The `
  name String!
  email String  #
  friends [Person]
}

type Query {
  getPerson(id: Integer): Person
}
```

This `gql` schema defines a custom type and exposes a simple query to retrieve
the person. The basic types that are defined are String, Integer, List, and
Boolean. You can define your own types to extend the schema which is what we
have done with the person type.

The Query type is a special type that indicates an 'method' you can call. The
nice thing about the gql language is that it is fairly readable and machines
love it because they can see the all the types of inputs and outputs. This
allows for a whole set of tooling that REST can not compete with.

First let's explore how we would use this, here is a example of using the
query to return just a single person's details:

**POST** /graphql

```gql
{
  query getPerson(id: 1) {
    name
    email
  }
}
```

RESPONSE:
```json
{
  "data": {
    "frank",
    "frank@tld.com"
  }
}
```

As you can see our request is a little verbose, but the response shape is the
same as the request. It will become a little easier to see that if we add in
the friend details:

**POST** /graphql

```gql
{
  getPerson(id: 1) {
    name
    email
    friend {
      name
      email
    }
  }
}
```

RESPONSE:
```json
{
  "data": {
    "getPerson": {
      "frank",
      "frank@tld.com",
      "friends": [
        {
          "name": "jane",
          "email": "jane@tld.com"
        },
        {
          "name": "john",
          "email": "john@tld.com"
        }
      ]
    }
  }
}
```

Perfect we now have a single query that is well documented (by the schema) and
it gives us just the data we need or want. On the backend the graphql server
does all the heavy lifting so we don't have to know where the data comes
from, all we know as a consumer is the types and the shape of the data. Which
is perfect for user interfaces. We want them to be simple and map to how our
customers have dictated how our data is being consumed. This allows us to
tweak our schema so that is benefits the UI how we want to use the api. Rather
than the other way, the REST api dictating how we can write our UI.

One of the ways this can become clear is taking advantage of graphql's strengths.
The data can come from anywhere, graphql doesn't actually care. Imagine if your
people data was stored in one data base, maybe an accounts service. Then imagine
you have an entirely separate service to register friendships. With GraphQL
you define the resolvers for your data and it is up to your imagination how
to accomplish that. Maybe you are one of those unlucky types that has to
interface with a soap endpoint? You just need to provide a method or function
that does the actual call and connect that to the schema.

What if we need to handle permissions for our application? Typically authorization
and authentication is handled by a different service. The api you have written
*should* check permissions for a given user and validate that they can do an
action and return an error if they can not do it. But what if you don't want
to be rude to users of your UI and show them a helpful message before they
try to click a button? Maybe disable the button or hide it completely?

Can we do this with GraphQL? Yes! What if certain people can create new users
in our system but some can't. You might have to do a query for the user data
and a call to your authorization service to see what permissions they have.
On the UI this could get tricky really fast as the number of permissions and
actions increases. But with GraphQL you can just add a custom type or field
for it. Here is an example:

```gql
type Permission {
  actionType String!  # create/read/delete/admin
  resource  String!   # users/posts/books/etc
}

type Person {
  id Integer!
  name String!
  email String
  friends [Person]
  permissions [Permission]
}

type Query {
  getPerson(id: Integer): Person
  getPermissions(personId: String!) [Permission]
}
```

Now when we query for our Person we can also get back the permissions they
have or we can query for an individual Person's permissions. We can even have
the best of both worlds and perform two queries for the price of one (it may
actually be more expensive but we'll talk performance later):

```gql
query {
  getPerson(id: 1) {
    name
    permissions {
      actionType
      resource
    }
  }

  getPermissions(personId: 1) {
    actionType
    resource
  }
}
```

RESPONSE:
```json
{
  "data": {
    "getPerson": {
      "frank",
      "permissions": [
        {
          "actionType": "create",
          "resource": "person"
        },
        {
          "actionType": "delete",
          "resource": "person"
        }
      ]
    },
    "getPermissions": [
      {
        "actionType": "create",
        "resource": "person"
      },
      {
        "actionType": "delete",
        "resource": "person"
      }
    ]
  }
}
```

Maybe that is not that useful, we would still need to implement a ton of logic
on the UI to handle these permissions. What if we do that work on the server?
Let's we calculate the permissions and the actions that are allowed. Here is
how this would look for our custom resolver that doesn't map directly to an
api call:

```python
from collections import namedtuple

Action = namedtuple('Action', 'permission, title, enabled, disabled_message')

ACTIONS = [
  # All actions are disabled by default
  Action('create', 'Create Person', False, 'You may not create People'),
  Action('delete', 'Delete Person', False, 'You may not delete People'),
  Action('view', 'View Person', False, 'You may not view People'),
]

def resolve_actions(_source, request):  # _source is unused in this example
    user = request.context.user
    permissions = get_permissions_for_user(user)  # get permissions somehow
    actions = []
    for action in ACTIONS:
      if action.permission in permissions:
        action.enabled = True
        actions.append(action)
```

Now the gql for our actions looks like:

```gql
type Action {
  title String!
  enabled Boolean!
  disabled_message String!
}

type Query {
  getActions() [Action]  # Uses the logged in user so it does not take arguments
}
```

Now the front end doesn't need to know anything about permissions it is all
handled by the GraphQL server. This makes the UI code super easy to reason
about, as it is just a view in your MVC. Remember MVC? Yeah Javascript has
been slowing attempting to kill that methodology with your redux and state
management. Why would you want your controller logic placed on your client
side Javascript? Let look at how we can wire this up. Even if you know nothing
about React or Javascript this should be fairly easy to follow:

```javascript
import React from 'react';
import { Query } from "react-apollo";

const GET_ACTIONS = `{
  getActions() {
    title
    enabled
    disabled_message
  }
}
`

export const ActionMenu = () => (
  <Query query={GET_ACTIONS} >
    {({ data }) => {
      return (
        <Menu>
          {data.getActions.map(item => (
            <ActionButton
                key={item.name}
                tooltip={item.enabled ? item.disabled_message : null}
                enabled={item.enabled}>
              {item.title}
            </ActionButton>
          ))}
        </Menu>
      );
    }}
  </Query>
);
```

This is as complicated your UI code should get. Each component or widget should
map to a GraphQL query and just display the results. They should not be concerned
with the nitty gritty details of where the data comes from or what your business
rules are to show or manipulate data. Continue reading as we cover all your
use cases.

[Go to Chapter One: Quick Start](chapterone.md)

[Table of Contents](table.md)
