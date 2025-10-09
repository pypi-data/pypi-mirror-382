# scse-toolkit

A toolkit for all other scse python applications.

## Run tests

First, start required services:

```bash
cd tests/
docker compose up
```

Then, run the tests:
> :warning: Check `test/conftest.py` for required environment variables.

```bash
poetry shell
pytest . [ENVIRONMENT_VARIABLES]
```