# Airplane Fuel Tracker REST API with Django

Django REST API for managing KAMI Airlines aircraft fuel
consumption and flight duration calculations.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![coverage badge](./coverage.svg)

License: MIT

## Documentation

For detailed information about the project, please check:

- [💻 Project Design Specifications](docs/project-design-specifications.md)
- [🛠️ Continuous Integration Setup](docs/continuous-integration.md)

## Running Locally

### Without Docker

#### Prerequisites

```bash
# Start PostgreSQL database
docker run -d \
    --name some-postgres \
    -e POSTGRES_PASSWORD=postgres \
    --rm \
    -p 5432:5432 \
    docker.io/postgres:16
```

#### Setup and Run

```bash
# Install dependencies
python -m pip install -r requirements/local.txt

# Setup database
python manage.py migrate

# Collect static files
python manage.py collectstatic
```

#### Development Commands

```bash
# Run tests
pytest

# Type checking
mypy fuel_tracker

# Test coverage
coverage run -m pytest
coverage html
```

### With Docker

#### Setup and Run

```bash
# Build the stack
docker compose -f docker-compose.local.yml build

# Start services
docker compose -f docker-compose.local.yml up

# Setup database
docker compose -f docker-compose.local.yml run --rm django python manage.py migrate
```

#### Development Commands

```bash
# Run tests
docker compose -f docker-compose.local.yml run --rm django pytest

# Type checking
docker compose -f docker-compose.local.yml run --rm django mypy

# Test coverage
docker compose -f docker-compose.local.yml run --rm django coverage run -m pytest
docker compose -f docker-compose.local.yml run --rm django coverage html
open htmlcov/index.html

```
