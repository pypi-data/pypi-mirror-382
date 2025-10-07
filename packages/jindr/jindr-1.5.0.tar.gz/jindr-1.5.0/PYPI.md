# JinDr - Local Docker Registry Manager

**JinDr** is a simple utility for deploying and managing a private docker
registry running on the local machine in a docker container.

Why?

In a nutshell ... to support building multi-platform docker images and provide a
simple test rig when you don't want to push a not-quite-ready docker build to
somewhere more exposed.

[![PyPI version](https://img.shields.io/pypi/v/jindr)](https://pypi.org/project/jindr/)
[![Python versions](https://img.shields.io/pypi/pyversions/jindr)](https://pypi.org/project/jindr/)
![PyPI - Format](https://img.shields.io/pypi/format/jindr)
[![GitHub License](https://img.shields.io/github/license/jin-gizmo/jindr)](https://github.com/jin-gizmo/jindr/blob/master/LICENCE.txt)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Genesis

**JinDr** was developed at [Origin Energy](https://www.originenergy.com.au)
as part of the *Jindabyne* initiative. While not part of our core IP, it proved
valuable internally, and we're sharing it in the hope it's useful to others.

Kudos to Origin for fostering a culture that empowers its people
to build complex technology solutions in-house.

[![Jin Gizmo Home](https://img.shields.io/badge/Jin_Gizmo_Home-d30000?logo=GitHub&color=d30000)](https://jin-gizmo.github.io)

## Capabilities

**JinDr** can create and manage a fully functional docker registry, running in
a docker container with persistent storage in the local filesystem. All of the
normal docker commands (pull, push etc.) work as expected.

*JinDr** provides a CLI with subcommands to:

* start and stop the registry
* view and delete registry contents
* copy docker images to AWS ECR or another docker registry.

## Installation and Usage

See [JinDr on GitHub](https://github.com/jin-gizmo/jindr).
