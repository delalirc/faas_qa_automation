# FAAS QA Automation - Centralized QA Repository

This repository contains all automated QA tests for the FAAS platform, maintained by the QA team.

## Overview

This is the **centralized QA approach** where:
- All tests live in this repository
- QA team maintains and updates tests
- Services trigger tests during deployment pipelines via CircleCI Orb
- Tests run in separate CircleCI pipeline

## Repository Structure

```
faas_qa_automation/
├── framework/              # Shared test framework
│   ├── api/               # API clients and authentication
│   ├── assertions/         # Custom assertions (financial, etc.)
│   ├── data/              # Test data generators
│   └── utils/              # Utilities (reporting, orchestration, etc.)
├── tests/                  # All test suites
│   ├── services/          # Service-specific tests
│   │   └── offer/         # Example: Offer service tests
│   │       ├── integration/  # Integration tests
│   │       └── e2e/          # E2E tests (Playwright)
│   ├── smoke/             # Smoke tests (quick health checks)
│   ├── journeys/          # Cross-service journey tests
│   └── regression/        # Regression test suites
├── scripts/               # Utility scripts
│   ├── wait_for_qa_tests.py    # Wait for test completion
│   └── check_qa_results.py     # Check test results
├── .circleci/             # CircleCI configuration
│   └── config.yml         # QA repository CI/CD
├── qa-automation-orb.yml  # CircleCI Orb definition
├── package.json           # Node.js dependencies (Playwright)
├── playwright.config.ts   # Playwright configuration
└── setup.py               # Python package setup
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- CircleCI account with API token

### Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
pip install -e .  # Install package in development mode
```

2. **Install Node.js dependencies (for Playwright):**
```bash
npm install
npx playwright install --with-deps
```

3. **Set environment variables:**
```bash
cp .env.example .env
# Edit .env with your values
```

Required environment variables:
- `BASE_URL`: Base URL for API testing (e.g., `https://dev.api.rcdevops.co.za`)
- `AUTH_TOKEN`: Authentication token for API calls
- `CIRCLECI_API_TOKEN`: CircleCI API token (for triggering tests)

### Running Tests Locally

```bash
# All tests
pytest

# Service-specific tests
pytest tests/services/offer/

# Integration tests only
pytest -m integration

# Financial tests
pytest -m financial

# Smoke tests
pytest -m smoke

# E2E tests (Playwright)
npx playwright test

# Specific service E2E tests
npx playwright test tests/services/offer/e2e/
```

## CircleCI Orb Deployment

This repository can be deployed as a CircleCI Orb for services to use.

### Publishing the Orb

1. **Create the orb in CircleCI:**
```bash
circleci orb create retail-capital/qa-automation
```

2. **Publish the orb:**
```bash
circleci orb publish qa-automation-orb.yml retail-capital/qa-automation@1.0.0
```

3. **Update orb version:**
```bash
circleci orb publish qa-automation-orb.yml retail-capital/qa-automation@1.1.0
```

### Using the Orb in Service Pipelines

Services can use the orb in their `.circleci/config.yml`:

```yaml
version: 2.1

orbs:
  base-orb: retail-capital/ci-base@6
  qa-trigger: retail-capital/qa-automation@1  # QA Automation Orb

workflows:
  faas-offer-development:
    jobs:
      - base-orb/setup
      - base-orb/python_pytest:
          name: Service Unit Tests
      
      # Centralized QA Tests
      - qa-trigger/run_service_tests:
          name: QA Integration Tests
          service: offer
          test_suite: integration
          requires: [Service Unit Tests]
          context:
            - faas-qa-secrets
      
      - qa-trigger/run_service_financial:
          name: QA Financial Tests
          service: offer
          requires: [QA Integration Tests]
          context:
            - faas-qa-secrets
      
      - qa-trigger/run_service_e2e:
          name: QA E2E Tests
          service: offer
          requires: [QA Financial Tests]
          context:
            - faas-qa-secrets
      
      - base-orb/terraform_init:
          requires: [QA E2E Tests]
      
      - base-orb/terraform_apply:
          requires: [Terraform Init]
      
      - qa-trigger/run_smoke_tests:
          name: Post-Deploy Validation
          service: offer
          requires: [Terraform Apply]
          context:
            - faas-qa-secrets
```

### Orb Jobs Available

- `qa-trigger/run_service_tests`: Run integration tests
- `qa-trigger/run_service_financial`: Run financial tests
- `qa-trigger/run_service_e2e`: Run E2E tests
- `qa-trigger/run_smoke_tests`: Run smoke tests (post-deploy)
- `qa-trigger/run_journey_tests`: Run cross-service journey tests

## Integration with Services

### How It Works

1. **Service Pipeline Triggers QA Tests:**
   - Service pipeline calls the QA orb
   - Orb triggers QA repository pipeline via CircleCI API
   - QA tests run in separate pipeline

2. **QA Tests Execute:**
   - Integration tests run first
   - Financial tests run next
   - E2E tests run last
   - Results are stored and reported

3. **Service Pipeline Waits:**
   - Service pipeline waits for QA tests to complete
   - If tests pass, deployment proceeds
   - If tests fail, deployment is blocked

### Required CircleCI Contexts

Services need to set up the following CircleCI context:

**Context: `faas-qa-secrets`**
- `CIRCLECI_API_TOKEN`: Token for triggering QA pipeline
- `AUTH_TOKEN`: Authentication token for API tests

## Test Organization

### Service Tests

Each service has its own directory under `tests/services/{service_name}/`:
- `integration/`: Integration tests (pytest)
- `e2e/`: E2E tests (Playwright)

### Test Markers

Tests are organized using pytest markers:
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.financial`: Financial calculation tests
- `@pytest.mark.e2e`: End-to-end tests
- `@pytest.mark.smoke`: Smoke tests
- `@pytest.mark.journey`: Cross-service journey tests
- `@pytest.mark.regression`: Regression tests

## Framework Components

### API Clients

Located in `framework/api/client.py`:
- `APIClient`: Generic API client
- `ServiceClient`: Base class for service clients
- `OfferClient`: Offer service client
- `ContractClient`: Contract service client
- `OrchestratorClient`: S2O orchestrator client

### Test Data Generators

Located in `framework/data/generators.py`:
- `generate_test_merchant()`: Generate test merchant data
- `generate_test_offer()`: Generate test offer data
- `generate_test_session()`: Generate S2O session data

### Utilities

- `framework/utils/test_orchestrator.py`: Test orchestration
- `framework/utils/reporting.py`: Test reporting and notifications
- `framework/utils/environment.py`: Environment helpers
- `framework/utils/notifications.py`: Slack/email notifications

## Scripts

### `scripts/wait_for_qa_tests.py`

Wait for QA tests to complete:
```bash
python scripts/wait_for_qa_tests.py --service offer --build-num 123
```

### `scripts/check_qa_results.py`

Check QA test results:
```bash
python scripts/check_qa_results.py --service offer --build-num 123 --fail-on-failure
```

## Documentation

- [QA Automation - Complete Guide](./QA_AUTOMATION.md): Comprehensive strategy, architecture, and implementation guide

## Contributing

### Adding Tests for a New Service

1. Create service directory:
```bash
mkdir -p tests/services/{service_name}/{integration,e2e}
```

2. Create test files:
```bash
touch tests/services/{service_name}/integration/test_api_endpoints.py
touch tests/services/{service_name}/e2e/test_journey.spec.ts
```

3. Add service client (if needed):
```python
# framework/api/client.py
class NewServiceClient(ServiceClient):
    def __init__(self, base_url=None, token=None):
        super().__init__('newservice', base_url, token)
```

### QA Team Workflow

1. Monitor test results from service deployments
2. Update tests when services change
3. Add new test cases for new features
4. Fix flaky tests
5. Communicate with service teams about failures

## Support

For questions or issues, contact the QA team or create an issue in this repository.
