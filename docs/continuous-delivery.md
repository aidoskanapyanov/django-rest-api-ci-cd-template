# Continuous Delivery Workflow

This project uses GitHub Actions for continuous delivery with an automated deployment workflow.

## Deployment Workflow (`deployment.yml`)

Triggers when:

- The `tests` workflow completes successfully
- Manually triggered via workflow dispatch

### Environment Variables

The workflow uses several secret environment variables for:

- Django configuration
- Database credentials
- Docker image tags
- Redis settings
- Server configuration

### Key Steps

1. **Build and Push Images**

   - Runs on Ubuntu latest
   - Authenticates with Docker Hub
   - Uses Docker Buildx for multi-platform builds
   - Builds and caches images for:
     - Django application
     - PostgreSQL database
     - Nginx web server
     - Traefik reverse proxy

2. **Deployment**
   - Deploys to Digital Ocean using Docker Swarm
   - Uses SSH for remote deployment
   - Applies production Docker Compose configuration

### Concurrency Control

- Prevents multiple deployments running simultaneously
- Cancels in-progress deployments when new ones are triggered

## Manual Deployment

You can manually trigger a deployment using GitHub CLI:

```bash
gh workflow run deployment
```

## Required Secrets

The following secrets must be configured in GitHub:

### Docker Hub Authentication

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

### Digital Ocean Server

- `DIGITAL_OCEAN_SSH_PRIVATE_KEY`
- `DIGITAL_OCEAN_IP_ADDRESS`

### Application Configuration

- `DJANGO_ACCOUNT_ALLOW_REGISTRATION`
- `DJANGO_ADMIN_URL`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_SECRET_KEY`
- `DJANGO_SECURE_SSL_REDIRECT`
- `DJANGO_SERVER_EMAIL`
- `DJANGO_SETTINGS_MODULE`

### Database Configuration

- `POSTGRES_DB`
- `POSTGRES_HOST`
- `POSTGRES_PASSWORD`
- `POSTGRES_PORT`
- `POSTGRES_USER`

### Service Configuration

- `REDIS_URL`
- `WEB_CONCURRENCY`

### Docker Images

- `DJANGO_IMAGE`
- `NGINX_IMAGE`
- `POSTGRES_IMAGE`
- `TRAEFIK_IMAGE`
