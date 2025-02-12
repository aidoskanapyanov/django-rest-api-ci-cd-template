# Continuous Integration Workflows

This project uses GitHub Actions for CI with two main workflows:

## 1. Tests Workflow (`tests.yml`)

Runs automated tests and code coverage checks when:

- Code is pushed to `main` branch
- Changes are made to core directories (fuel_tracker, tests, config, etc.)
- Manually triggered

Key steps:

- Builds Docker stack
- Validates database migrations
- Runs pytest suite
- Generates coverage reports
- Uploads coverage artifacts

## 2. Pre-commit Workflow (`pre-commit.yml`)

Runs code quality checks when:

- Code is pushed to `main` branch
- Manually triggered

Key steps:

- Sets up Python environment
- Runs pre-commit hooks for linting and formatting

## Manual Workflow Dispatch

You can manually trigger workflows using GitHub CLI:

```bash
# Trigger tests workflow
gh workflow run tests.yml

# Trigger pre-commit workflow
gh workflow run pre-commit.yml
```

## Working with Coverage Reports

Download and view the latest coverage report:

```bash
# List workflow runs to get run ID
gh run list --workflow=tests.yml

# Download coverage artifact (replace RUN_ID)
gh run download RUN_ID -D cov-arts --name coverage-report

# View coverage report in browser
python -m http.server -d cov-arts
```

Then open `http://localhost:8000` in your browser to view the coverage report.

Note: Coverage artifacts are retained for 7 days.
