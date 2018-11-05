# Pygraph

GraphQL for people who like python and dislike Javascript stealing all our
business logic!

# Documentation

We pride ourselves on having through documentation, explaining our reasons for
all the decissions we made. We wrote a whole book before we wrote a single line
of code!

[See Documentation](./docs)

# Why Pygraph?

We wanted to make the world a better place, but we are programmers so we settled
on making the web fun again. Too much attention has been given to Javascript
client libraries. They all seem to compete on size and speed and features but
most of them do not solve any of the actual problems you have. So while the
todo application is quick and easy to follow the hard parts take a long time
to complete. For starters Javascript use to be simple and it did not require
using a transpiler. It was mostly JQuery and it sort of worked but it didn't
get in your way.

Now a days if you want a fancy single page application you need to invest a
good week or so planning out all the tools you will need to assemble your site.
Every decision is full of sorrow and doubt as you google for the latest trends
or how to setup unit tests. Or searching for a bootstrapped version of the
library you like.

Say for example you want to have hot reloading developer experience you need
to organize your code in a way that allows this to work. If you are familiar
with python web applications they usually have a dev mode that you can start.
With webpack and parsel you can have the hot reloading but that doesn't play
well with your python library. So you have to either do tricks or just give
up complete control to your client side Javascript. It is just not easy to
have a simple web page served by a python web framework along side your
dynamic pages that require a ton of interaction.

Why did we let the Javascript developers take over all this control out from
under our noses?

Pygraph is our way of taking back the web. What if I told you, you can have
your cake and eat it too? Too good to be true? No it is all possible with a
few simple tools and you can rescue your sanity once again. The best part is
as the javascript becomes smaller you have greater control over the page speed
once again. React and others can now do server side rendering to reduce the
amount of time it takes to render a page. But you can achieve the same boost
in speed boost using pygraph. All without having to run node.

Is Pygraph unique or only for Python?

No, while pygraph is for python if you read the book you will notice that
there is nothing specific about Python that is required. The magic all happens
with graphql. You can use any language you want as your graphql server. We just
happen to like Python so we wrote a framework to make it easy to replicate our
designs.

At the heart of it graphql is the glue holding the system together how you
inject data into graphql is entirely up to you. And how little you use is up
to you too. It could be that you really like managing 1500 npm modules just
so that you can render :ghost: gifs on the webpack command line. I guess what
ever floats your boat. If you are like me and don't want to be dependant on
*EVERYTHING* working (yarn.lock file?) then you should reduce the number of
libraries you use. That includes this one, don't use it if all you need is a
single page.

Our Philosophy:
1. Make your site easy to maintain.
2. Document your code.
3. Don't lock yourself into a framework.
4. Be happy!

