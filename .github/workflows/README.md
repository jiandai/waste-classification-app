# GitHub Actions CI/CD Workflows

This repository uses GitHub Actions for continuous integration and deployment.

## Workflows

### Main CI Workflow (`ci.yml`)

The main CI workflow runs on every push to `main` and on all pull requests. It includes:

#### Backend Tests (`backend-lint-and-test`)
- Python 3.11 setup with pip caching
- Installs dependencies from `backend/requirements.txt`
- Runs ruff linting (errors/warnings, allows long lines)
- Executes pytest test suite with stub vision provider

#### Docker Build (`docker-build`)
- Builds the Docker image using `Dockerfile`
- Starts a test container with stub vision provider
- Validates the `/health` endpoint

#### Mobile Check (`mobile-check`)
- Node.js 20 setup with npm caching
- Installs mobile dependencies with `npm ci`
- Validates Expo configuration

### Component-Specific Workflows

#### Backend CI (`backend-ci.yml`)
Runs only when backend files change:
- Triggers on changes to `backend/**`, `Dockerfile`, or the workflow file itself
- Same jobs as main CI but backend-focused

#### Mobile CI (`mobile-ci.yml`)
Runs only when mobile files change:
- Triggers on changes to `mobile/**` or the workflow file itself
- Mobile-specific linting and build checks

## Running Tests Locally

### Backend Tests

```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx ruff

# Run tests
VISION_PROVIDER=stub pytest -v

# Run linter
ruff check . --select E,F,W --ignore E501
```

### Docker Build

```bash
# Build the image
docker build -t waste-classification-app:test .

# Test the container
docker run -d -p 8000:8000 -e VISION_PROVIDER=stub waste-classification-app:test
sleep 10
curl http://localhost:8000/health
```

### Mobile Checks

```bash
cd mobile
npm ci
npx expo config --json
```

## Environment Variables

The workflows use the following environment variables:

- `VISION_PROVIDER=stub`: Uses stub vision provider for testing (no API calls)
- `OPENAI_API_KEY=test-key`: Dummy key for tests (not used in stub mode)

## Test Coverage

Current test coverage includes:

### Backend (`backend/tests/`)
- **`test_main.py`**: API endpoint tests
  - Health check
  - Classification endpoint with valid/invalid inputs
  - Clarification endpoint
  - File size/type validation
  - Error handling
  
- **`test_rules.py`**: Decision engine tests
  - Confidence bucket calculations
  - Bin classification logic (recycling, organics, trash, special handling)
  - Special handling categories (batteries, e-waste, HHW, sharps)
  - Contamination clarification
  - Rationale generation

### Coverage Stats
- 22 passing tests
- Tests cover main API endpoints, rules engine, and error cases
- All tests run with stub vision provider (no external API dependencies)

## CI Status

You can check the CI status on the [Actions tab](../../actions) of the repository.

## Adding New Tests

To add new tests:

1. Create test files in `backend/tests/` following the pattern `test_*.py`
2. Use pytest fixtures and async test support as needed
3. Ensure tests run with `VISION_PROVIDER=stub`
4. Run locally before pushing: `cd backend && pytest -v`

## Troubleshooting

### Tests Failing Locally

```bash
# Make sure you have the right Python version
python --version  # Should be 3.11+

# Reinstall dependencies
cd backend
pip install --upgrade pip
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx ruff
```

### Docker Build Failing

```bash
# Check Docker is running
docker --version

# Clean up old images
docker system prune -a

# Try building again
docker build -t waste-classification-app:test .
```

### Mobile Config Failing

```bash
cd mobile

# Clean install
rm -rf node_modules package-lock.json
npm install

# Check expo config
npx expo config --json
```

## Future Enhancements

Planned improvements:

- [ ] Code coverage reporting with codecov
- [ ] Security scanning with Snyk or Dependabot
- [ ] Automated deployment to Render/Fly.io on main branch
- [ ] Performance benchmarks
- [ ] End-to-end tests with Playwright
- [ ] Mobile build tests with EAS Build
