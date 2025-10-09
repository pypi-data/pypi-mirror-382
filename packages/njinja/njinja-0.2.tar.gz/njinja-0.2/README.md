# njinja

`njinja` is a general-purpose lightweight meta-build system for
[Ninja](https://ninja-build.org/).

It is for people who:

- need the flexilibity of `make(1)` (e.g. wildcards) but want to migrate away
  from its unclean language

- need the lightweight and principled design of `ninja(1)` but need a equally
  lightweight (and principled) way to generate its build files

- have an unusual project structure that cannot be cleanly handled by other
  common meta-build systems for ninja, that are too special-purpose or focus on
  a particular programming language that isn't what your project actually uses.

Install via pip:

~~~~
$ pip3 install -U njinja
~~~~

## Usage

1. Write your [Ninja build file](https://ninja-build.org/manual.html) as a
[Jinja template](https://jinja.palletsprojects.com/en/stable/templates/), named
(e.g.) `build.ninja.j2`. Within this template, you may refer to variables that
contain build inputs that cannot be known (or are inconvenient to know) in
advance.

2. Write a python build script, named (e.g.) `build.py`, that uses our `njinja`
library to calculate these build inputs, populate the template with them,
create a `build.ninja` file, and call ninja on this file all in one step.

See [here](https://github.com/infinity0/njinja/blob/master/example) for our
basic example, that showcases a few different ways of calculating these build
variables. Adapt this to whatever is suitable for your project.
