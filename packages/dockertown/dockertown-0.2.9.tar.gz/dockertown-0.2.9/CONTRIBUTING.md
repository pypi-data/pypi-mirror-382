# Contributing to Dockertown

You want to make Dockertown better? Great! Help is always welcomed!

In this document, we'll try to explain how this package works internally and how you can 
contribute to it.

First things first, if it's your first pull request to an open-source project, head to
https://github.com/firstcontributions/first-contributions. This guide will explain 
how to open a pull request in a github repository that you don't own.

## Building the docs

All docstring are fetched and put in templates. Everything is done in markdown, 
with the help of [keras-autodoc](https://duckietown.github.io/keras-autodoc/) and
[mkdocs](https://www.mkdocs.org/).

#### First install the dependencies:

```
pip install keras-autodoc mkdocs Sphinx==3.5.4
```

#### Generate the documentation files and serve them
```
cd ./docs/
python autogen.py && mkdocs serve
```

#### Open your browser

http://localhost:8000


## Running the tests

Install all dependencies and install dockertown in editable mode:
```
pip install -r requirements.txt -r tests/test-requirements.txt
pip install -e ./
```

Then:

```bash
pytest -v ./tests/
```


## Exploring the codebase

The sources are in the `dockertown` directory. Everytime a class has something to 
do with the Docker daemon, a `client_config` attribute is there and must be passed around.

This `client_config` tells the Docker CLI how to connect to the daemon. 
You can think of it of the collection of all the arguments that are at the start of the CLI.
For example `docker -H ssh://my_user@my_ip ...`.

Each sub-component of the CLI is in a separate directory. 

#### Component structure

The structure is the following for calling `docker image ...`.

`ImageCLI` is in charge of calling the `docker image` commande. This class appears when you call
```python
from dockertown import docker
print(docker.image)
```
`ImageCLI` is in `dockertown/components/image/cli_wrapper.py`.

`Image` is in charge of holding all the metadata of a Docker image and has all 
the attributes that you could find by doing `docker image inspect ...`.

It has some methods for convenience. For example:

```python
from dockertown import docker

my_ubuntu = docker.pull("ubuntu")

my_ubuntu.remove()
# is the same as
docker.image.remove(my_ubuntu)
```

Since `Image` has all the information you can find with `docker image inspect ...`, we need 
to parse the json output. All parsing models are found in `dockertown/components/image/models.py`.
