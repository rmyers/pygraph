# Legacy Graphql Tutorial

This is an example of updating a old legacy site to using graphql. It is
using an 'ancient' version of Django 1.6 and still on Python 2.7. While
you may not have it that bad, I'm guessing there are many people who will
stumble upon a old site that they wish to update.

Well look no further this will be your guide to the new future. First steps
are to expose a graphql endpoint. Then create schema and resolvers for all
of your data then slowly convert your pages to use the graphql api rather
than sending data down with the context.

The way we have structured this tutorial you will see how to setup your
application in a way that will be easier to maintain going forward. Or at
least that is the hope. Any decision made at any point could be the wrong
one and time will tell if we made the world a better place or not.

The main goal of this is the reduce the dependency on third party tools as
much as possible for your main business logic. De-couple your Django models
from your views and separate concerns. Don't get me wrong third party tools
can help you get a site up quickly. They also make it incredibly hard to
update any single piece of your stack. You usually end up with a mess in the
end and you might have been better off learning how something works and
implementing it yourself. Then when you go to upgrade, you only have to fix
your code.

Long story short, we wrote a site a few years ago and took shortcuts to get
our site up. Now we need to update and it is hard.

## Sample Application

This is a simplified version of the julython website. Wich you can view the
actual source on github https://github.com/julython/julython.org

The sample application only has a game and commit models which is great
for all things we need.

To start we have included a Makefile to guide you on your path. Simply run:

```bash
$ make run
```

If you get stuck you can at any time run:

```bash
$ make clean
$ make run
```

**FYI:** Makefiles are a good way to share setup logic with other people `make`
is installed on most developer machines or is easy[1] to install. Make is great
for creating files (which is it's job) it will scan the directory and see if
a file needs to be created. If is does not it just skips over that target.
We can use this to our advantage with the example database and virtualenv. If
they do not exist the makefile targets will create them.

[1]: 'easy' applies to all developers who do not use windows (you are on
your own, good luck! try docker :shrug:)

To get started simply clone down this repo and launch the demo final product:

```bash
$ git clone git@github.com:rmyers/pygraph.git
$ cd pygraph/tutorial/legacy
$ make run
```

Now simply browse to http://localhost:8000/api/v2/graphql to view the
playground.

