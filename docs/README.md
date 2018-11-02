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
    },{
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
simple easy to read and we are done.
