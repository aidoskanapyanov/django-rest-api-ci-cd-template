# Airplane Fuel Tracker REST API with Django

Django REST API for managing Airlines aircraft fuel
consumption and flight duration calculations.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![coverage badge](./coverage.svg)

[<img src="images/buymecoffee.png"  alt="buymeacoffee-white-badge" style="width: 160px;">](https://www.buymeacoffee.com/aidosk)

## 📚 Documentation

For detailed information about the project, please check:

- [💻 Project Design Specifications](docs/project-design-specifications.md)<br>
  Architecture, data models, and API endpoints documentation

- [🛠️ Continuous Integration Setup](docs/continuous-integration.md)<br>
  Pre-commit hooks configuration and automated testing pipeline

- [🚀 Continuous Delivery Setup](docs/continuous-delivery.md)<br>
  Docker image build, DockerHub publishing, and DigitalOcean Docker Swarm deployment

- [🎨 Style Guide](docs/style-guide.md)<br>
  Project code style guide: commit messages, release versioning

## 🛠️ Tech Stack

### Backend Framework & API

- **Django**: Python web framework for rapid development
- **Django REST Framework**: Powerful toolkit for building Web APIs
- **DRF-Spectacular**: OpenAPI/Swagger documentation generator

### Testing & Quality Assurance

- **pytest**: Feature-rich testing framework
- **pytest-django**: Django-specific testing utilities
- **Coverage.py**: Code coverage measurement
- **pre-commit**: Git hooks framework for code quality checks

### Security & SSL

- **Traefik**: Modern reverse proxy and load balancer
- **Let's Encrypt**: Automatic SSL certificate provisioning
  - ACME protocol for automated certificate issuance and renewal
  - Zero-downtime certificate rotation

### Code Quality & Formatting

- **Black**: Uncompromising Python code formatter
- **Ruff**: Extremely fast Python linter
- **mypy**: Static type checker

### Development & Deployment

- **Docker**: Container platform
- **Docker Compose**: Multi-container development environments
- **Docker Swarm**: Container orchestration for production
  - Zero-downtime deployments with rolling updates
  - Automatic service rollbacks on failure
  - Health checks and self-healing capabilities
- **GitHub Actions**: CI/CD automation
- **Neovim**: Blazingly fast, extensible code editor

### Database

- **PostgreSQL**: Robust relational database

## 🏃 Running Locally

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

# Run server, and open http://localhost:8000/api/docs
python manage.py runserver
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

## ☕ Author

- **Aidos Kanapyanov** ([aidos.kanapyanov2@gmail.com](mailto:aidos.kanapyanov2@gmail.com))
- 💼 [LinkedIn Profile](https://www.linkedin.com/in/aidos-kanapyanov/)

## ⚖️ License

This project is licensed under the MIT License.
