# Hyperion

Hyperion is a CLI tool and rest api that facilitates searching for crime data
at specific geographical locations in the UK.

### Getting Started

Simply pip install the package, and then get started with

    pip install hyperion-cli
    hyperion --help

### Server

Running the server can be done either through the cli app, or via a the
official docker container. There are some environment variables that
can be used to set the host and port (but are overridden by the CLI args).

```bash
HYPERION_HOST=0.0.0.0
HYPERION_PORT=8080
```

### Data

Data is aggregated and cached from the following sources:

- BikeRegister
- UK Police
- Google maps
- Twitter RSS
- UK Postcodes
- Wikipedia

### Web App

A [web app](https://github.com/arlyon/hyperion-web) for interacting
with this API is available as well.

### Run Tests

Running tests and linters can be done through poetry:

```
poetry run pytest test/
poetry run pytest --flake8 --mypy hyperion_cli
```
