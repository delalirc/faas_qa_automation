# FAAS QA Automation - Centralized QA Strategy

## Executive Summary

This document presents the **Centralized QA Automation Strategy** for the FAAS platform. This approach establishes a dedicated QA team that maintains all automated tests in a central repository, with services triggering these tests during their deployment pipelines via CircleCI Orbs.

### Key Benefits

✅ **Specialization** - QA team becomes experts in testing  
✅ **Consistency** - Uniform testing approach across all 25+ services  
✅ **Independence** - Tests are independent of service code changes  
✅ **Focus** - Service teams focus on features, QA team focuses on quality  
✅ **Comprehensive** - Partner-specific journey tests cover all integration tiers  
✅ **Scalability** - Easy to add new services and partners  

---

## Table of Contents

1. [Strategy & Philosophy](#strategy--philosophy)
2. [Architecture Overview](#architecture-overview)
3. [Test Types & Organization](#test-types--organization)
4. [Implementation Guide](#implementation-guide)
5. [Journey Tests - Partner-Specific E2E](#journey-tests---partner-specific-e2e)
6. [Deployment Integration](#deployment-integration)
7. [Examples](#examples)

---

## Strategy & Philosophy

### What is Centralized QA?

**Centralized QA** means:
- A dedicated QA team owns and maintains all automated tests
- Tests live in a central repository (`faas_qa_automation`) separate from service code
- Services trigger centralized tests during their deployment pipelines
- QA team is responsible for test quality, maintenance, and strategy
- Service teams focus on development; QA team focuses on testing

### Core Principles

1. **Separation of Concerns**
   - Service teams: Build features
   - QA team: Test features

2. **Test Independence**
   - Tests are not tied to service codebases
   - Tests can evolve independently
   - Service changes don't break test infrastructure

3. **Comprehensive Coverage**
   - Integration tests: API contract validation
   - E2E tests: Internal service journeys
   - Journey tests: Partner-specific complete flows
   - Regression tests: Orchestrate all journeys

4. **Environment-Specific Strategy**
   - **Development**: Fast feedback, unit tests only
   - **UAT**: Full QA validation after deployment (test new code)
   - **Production**: Smoke tests only (already validated in UAT)

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              CENTRALIZED QA REPOSITORY                           │
│              (faas_qa_automation)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              QA Team Maintains Tests                      │  │
│  │                                                           │  │
│  │  tests/                                                   │  │
│  │  ├── services/          # Service-specific tests          │  │
│  │  │   ├── offer/        # faas_offer tests               │  │
│  │  │   ├── contract/     # faas_contract tests            │  │
│  │  │   └── ...           # All 25+ services               │  │
│  │  ├── journeys/         # Partner-specific journeys       │  │
│  │  │   ├── test_atm_journey.spec.ts                       │  │
│  │  │   ├── test_fnb_journey.spec.ts                       │  │
│  │  │   └── ...           # All 10+ partners               │  │
│  │  ├── regression/       # Regression orchestration        │  │
│  │  └── smoke/            # Smoke tests                    │  │
│  │                                                           │  │
│  │  framework/            # Shared test framework          │  │
│  │  qa-automation-orb.yml  # CircleCI Orb definition        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ Triggered via CircleCI Orb
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ faas_offer   │   │faas_contract │   │faas_integration│
│ Pipeline     │   │ Pipeline     │   │ Pipeline      │
│              │   │              │   │               │
│ Uses Orb:    │   │ Uses Orb:    │   │ Uses Orb:     │
│ qa-trigger/  │   │ qa-trigger/  │   │ qa-trigger/   │
│ run_service_ │   │ run_service_ │   │ run_service_  │
│ tests        │   │ tests        │   │ tests         │
└──────────────┘   └──────────────┘   └──────────────┘
```

### Key Components

1. **Central Test Repository** (`faas_qa_automation`)
   - Single source of truth for all tests
   - Owned and maintained by QA team
   - Version controlled independently

2. **CircleCI Orb** (`retail-capital/qa-automation@1`)
   - Reusable package of CircleCI configuration
   - Services import orb to trigger QA tests
   - Published from QA repository

3. **Service Integration**
   - Services add orb to their CircleCI config
   - Services trigger QA tests during deployment
   - QA tests run in separate pipeline

4. **Test Execution**
   - QA repository pipeline runs tests
   - Results reported back to service pipeline
   - Service pipeline blocks on test failures

---

## Test Types & Organization

### Test Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│                    TEST TYPES                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Integration Tests (API Contract Tests)               │
│     └─ tests/services/{service}/integration/            │
│                                                          │
│  2. E2E Tests (Internal Service Journeys)               │
│     └─ tests/services/{service}/e2e/                    │
│                                                          │
│  3. Journey Tests (Partner-Specific Comprehensive)     │
│     └─ tests/journeys/                                  │
│                                                          │
│  4. Regression Tests (Orchestration)                    │
│     └─ tests/regression/                                │
│                                                          │
│  5. Smoke Tests (Quick Health Checks)                   │
│     └─ tests/smoke/                                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 1. Integration Tests

**Purpose:** API Contract Testing - Verify all API endpoints work correctly

**Location:** `tests/services/{service}/integration/`

**What They Test:**
- ✅ Individual API endpoints in isolation
- ✅ Request/response formats
- ✅ Status codes and error handling
- ✅ Data structures and field presence
- ✅ Authentication/authorization

**Example:**
```python
@pytest.mark.integration
class TestOfferAPI:
    def test_get_offers_for_partner(self, offer_client, partner_id):
        """Test GET /offer/{partner_id}/offers endpoint"""
        response = offer_client.get_offers(partner_id)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
```

**When They Run:** Every deployment (UAT and Production)

---

### 2. E2E Tests

**Purpose:** Internal Service Journey Testing - Verify complete workflows within a single service

**Location:** `tests/services/{service}/e2e/`

**What They Test:**
- ✅ Multi-step processes within one service
- ✅ Business logic flows
- ✅ State transitions
- ✅ Complete user journeys (within service)

**Example:**
```python
@pytest.mark.e2e
class TestOfferJourney:
    def test_offer_validation_journey(self, offer_client, partner_id):
        """Test complete offer validation flow"""
        # Step 1: Get offers
        offers = offer_client.get_offers(partner_id)
        offer = offers.json()[0][0]
        
        # Step 2: Get offer details
        offer_details = offer_client.get_offer(partner_id, offer_id=offer['id'], extended=True)
        
        # Step 3: Validate offer
        validation = offer_client.validate_offer(partner_id, offer['id'], {...})
        
        # Step 4: Get validation result
        validation_result = offer_client.get_offer_validation(partner_id, validation.json()['offerValidationID'])
        
        assert validation_result.json()['isValidated'] == True
```

**When They Run:** Every deployment (UAT and Production)

---

### 3. Journey Tests (Partner-Specific)

**Purpose:** Partner-Specific Comprehensive End-to-End Testing - Verify complete flow for each partner

**Location:** `tests/journeys/`

**What They Test:**
- ✅ Partner-specific journeys (one test file per partner)
- ✅ Get partner config from partner API (offer URL/cloudfront domain)
- ✅ Get offer from offer service
- ✅ Frontend validation with Playwright (partner branding, sliders, screens)
- ✅ Complete onboarding flow (3 screens)
- ✅ Contract creation and verification
- ✅ CRM integration (Salesforce verification in UAT)
- ✅ Test activation (invoice number, CRM number)
- ✅ Sage integration verification
- ✅ Partner external API integration verification

**Example Structure:**
```typescript
// tests/journeys/test_atm_journey.spec.ts
test('should complete full ATM partner journey', async ({ request, page }) => {
    // Step 1: Get partner config
    const config = await getPartnerConfig('5e9d531c-791b-463a-aeea-233eb7d04a9b');
    const offerUrl = config.offerConfig.url; // e.g., "atm.com"
    
    // Step 2: Get offer
    const offers = await getOffers(partnerId, { page: 1, pageSize: 1 });
    const offerId = offers[0][0].id;
    
    // Step 3: Frontend validation (Playwright)
    await page.goto(`${offerUrl}/offer?offerID=${offerId}`);
    await expect(page.locator('.partner-logo')).toBeVisible(); // ATM logo
    await expect(page.locator('.slider')).toBeVisible(); // Screen 1 sliders
    
    // Step 4: Complete onboarding (3 screens)
    await completeOnboarding(page);
    
    // Step 5: Contract creation
    const contract = await waitForContract(offerId);
    
    // Step 6: CRM verification (query Salesforce in UAT)
    await verifyCRMSubmission(contract.id);
    
    // Step 7: Test activation
    await activateContract(contract.id, {
        invoiceNumber: 'TEST-INV-001',
        crmNumber: 'TEST-CRM-001'
    });
    
    // Step 8: Sage integration
    await verifySageIntegration(contract.id);
    
    // Step 9: Partner API integration
    await verifyPartnerNotification(partnerId, contract.id);
});
```

**When They Run:** UAT deployments, scheduled regression runs

---

### 4. Regression Tests

**Purpose:** Test Orchestration - Orchestrate running all partner journey tests

**Location:** `tests/regression/`

**Key Point:** Regression tests are NOT a separate test suite - they orchestrate running all partner journeys.

**What They Do:**
- ✅ Run all partner journey tests
- ✅ Run Tier 1 partner journeys only (for faster execution)
- ✅ Each journey covers all tiers (onboarding, CRM, Sage, partner API)

**Example:**
```python
@pytest.mark.regression
class TestTier1Regression:
    def test_all_partner_journeys(self):
        """Run all partner journey tests"""
        # Executes: npx playwright test tests/journeys/
        subprocess.run([
            'npx', 'playwright', 'test',
            'tests/journeys/',
            '--reporter=list',
        ])
```

**When They Run:** After service deployments, scheduled (nightly/weekly)

---

### 5. Smoke Tests

**Purpose:** Quick Health Checks - Fast validation that services are operational

**Location:** `tests/smoke/`

**What They Test:**
- ✅ Quick health check endpoints
- ✅ Verify services are up and responding
- ✅ Basic connectivity tests
- ✅ Fast execution (< 1 minute)

**When They Run:** Post-deployment (UAT and Production)

---

## Implementation Guide

### How to Add QA Automation to a Service

This section shows exactly how to implement centralized QA for a new service.

#### Step 1: Add CircleCI Orb to Service

Add the QA automation orb to your service's `.circleci/config.yml`:

```yaml
version: 2.1

orbs:
  base-orb: retail-capital/ci-base@6
  qa-trigger: retail-capital/qa-automation@1  # Add this line

workflows:
  faas-{service}-uat:
    jobs:
      # ... existing jobs ...
```

#### Step 2: Add QA Test Jobs to UAT Workflow

Add QA test jobs **AFTER** deployment and migration:

```yaml
workflows:
  faas-{service}-uat:
    jobs:
      # Existing jobs
      - base-orb/setup:
          name: Setup
      
      - base-orb/python_pytest:
          name: Pytest  # Service unit tests
      
      - base-orb/setup_deploy:
          requires: [Pytest]
          name: Deploy setup - UAT
      
      - base-orb/terraform_init:
          requires: [Deploy setup - UAT]
          name: Terraform Init and Plan - UAT
      
      - hold-tf:
          type: approval
          requires: [Terraform Init and Plan - UAT]
      
      - base-orb/terraform_apply:
          requires: [hold-tf]
          name: Terraform Apply - UAT
      
      - base-orb/migration:
          requires: [Terraform Apply - UAT]
          name: Run Migration - UAT
      
      # ==========================================
      # Centralized QA Tests (AFTER deployment)
      # QA tests validate service in UAT after new code is deployed
      # ==========================================
      - qa-trigger/run_service_tests:
          name: QA Integration Tests
          service: {service_name}  # e.g., "offer", "contract"
          test_suite: integration
          environment: uat
          requires:
            - Run Migration - UAT  # Run after migration
          context:
            - faas-qa-secrets
      
      - qa-trigger/run_service_e2e:
          name: QA E2E Tests
          service: {service_name}
          environment: uat
          requires:
            - QA Financial Tests
          context:
            - faas-qa-secrets
      
      # ==========================================
      # Post-Deploy Validation
      # ==========================================
      - qa-trigger/run_smoke_tests:
          name: Post-Deploy Smoke Tests
          service: {service_name}
          environment: uat
          requires:
            - QA E2E Tests  # Run after all QA tests
          context:
            - faas-qa-secrets
      
      - hold-promotion:
          type: approval
          requires:
            - Post-Deploy Smoke Tests  # Now depends on smoke tests
      
      - base-orb/promotion:
          deploy_environment: UAT
          requires:
            - hold-promotion
```

#### Step 3: Add Smoke Tests to Production Workflow

For Production, only add smoke tests (QA tests already validated in UAT):

```yaml
workflows:
  faas-{service}-production:
    jobs:
      # ... existing jobs ...
      
      - base-orb/migration:
          requires: [Terraform Apply - Production]
          name: Run Migration - Production
      
      # ==========================================
      # Post-Deploy Validation (Production)
      # Only smoke tests - QA tests already validated in UAT
      # ==========================================
      - qa-trigger/run_smoke_tests:
          name: Post-Deploy Smoke Tests
          service: {service_name}
          environment: prod
          requires:
            - Run Migration - Production
          context:
            - faas-qa-secrets
```

#### Step 4: Set Up CircleCI Context

Create or update the `faas-qa-secrets` context in CircleCI with:

- `CIRCLECI_API_TOKEN`: Token for triggering QA pipeline
- `AUTH_TOKEN`: Authentication token for API tests

#### Step 5: Notify QA Team

Contact the QA team to:
1. Add tests for your service to `faas_qa_automation` repository
2. Create integration tests in `tests/services/{service_name}/integration/`
3. Create E2E tests in `tests/services/{service_name}/e2e/`
4. Add service-specific API client if needed

---

## Journey Tests - Partner-Specific E2E

### Overview

Journey tests are **partner-specific comprehensive end-to-end tests** that verify the complete flow for each partner. Each journey covers all tiers of integration.

### Journey Flow

Each partner journey follows this complete flow:

```
1. Get Partner Config
   └─> Call partner API to get config (includes offer URL/cloudfront domain)

2. Get Offer
   └─> Call offer service: GET /offer/{partner_id}/offers?page=1&pageSize=1

3. Frontend Validation (Playwright)
   └─> Navigate to: {offerUrl}/offer?offerID={offerId}
   └─> Verify partner branding (logo)
   └─> Verify screen 1 has sliders
   └─> Verify faas_client and faas_client_interface are loaded

4. Complete Onboarding (3 screens)
   └─> Screen 1: Offer selection
   └─> Screen 2: Additional information
   └─> Screen 3: Final confirmation
   └─> Submit onboarding

5. Contract Creation
   └─> Poll for contract creation
   └─> Verify contract exists

6. CRM Submission Verification
   └─> Query Salesforce in UAT
   └─> Verify contract was pushed to CRM

7. Test Activation
   └─> Activate contract with test account
   └─> Use test invoice number and CRM number

8. Sage Integration Verification
   └─> Verify contract synced to Sage

9. Partner API Integration Verification
   └─> Verify partner was notified via external API
```

### Partner-Specific Test Files

Each partner has their own journey test file:

- `test_atm_journey.spec.ts` - ATM partner journey
- `test_fnb_journey.spec.ts` - FNB partner journey
- `test_netcash_journey.spec.ts` - NetCash partner journey
- `test_tabbs_journey.spec.ts` - Tabbs partner journey
- `test_kazang_journey.spec.ts` - Kazang partner journey
- `test_ikhokha_journey.spec.ts` - iKhokha partner journey
- `test_takealot_journey.spec.ts` - Takealot partner journey
- `test_payfast_journey.spec.ts` - PayFast partner journey
- `test_korridor_journey.spec.ts` - Korridor partner journey

### Partner IDs

Partner IDs are defined in each journey test:

- **ATM**: `5e9d531c-791b-463a-aeea-233eb7d04a9b`
- **FNB**: `82c1c0a8-a203-4a73-8750-cf2dfe21835d`
- **NetCash**: `30f50c8b-7b88-49c1-8b61-ca93b8f6ea7e`
- **Tabbs**: `960f7a46-180d-4615-a87a-31e0dbeb1b64`
- **Kazang**: `1d51ef18-0d07-403b-a499-3fd2296532ef`
- **iKhokha**: `675911fa-95ad-4fdd-adea-802240c79887`
- **Takealot**: `e01c1138-d4c3-4b5d-8ca2-ea1034b91f9e`
- **PayFast**: `c7b09cd3-a52f-468b-93a7-3c438036a50c`
- **Korridor**: `449703d7-913d-4798-aa28-05adfe7e1ef5`

### Running Journey Tests

```bash
# Run all journeys
npx playwright test tests/journeys/

# Run specific partner journey
npx playwright test tests/journeys/test_atm_journey.spec.ts

# Run via regression tests
pytest tests/regression/test_tier1_services.py::TestTier1Regression::test_all_partner_journeys
```

---

## Deployment Integration

### Environment-Specific Strategy

#### Development Environment

**Strategy:** Fast feedback, no QA overhead

```
Setup → Unit Tests → Deploy → Migration → (Done)
```

**No QA tests** - Focus on speed and unit tests

---

#### UAT Environment

**Strategy:** Full QA validation after deployment (test new code)

```
Setup → Unit Tests → Deploy → Migration → QA Tests (new code) → Smoke Tests
```

**QA Tests Run:**
- ✅ Integration Tests (after migration)
- ✅ Financial Tests (after integration)
- ✅ E2E Tests (after financial)
- ✅ Smoke Tests (after E2E)

**Rationale:**
- Deploy new code to UAT first
- Run full QA tests against the newly deployed code
- Catch issues before production
- If QA passes, new code is validated

---

#### Production Environment

**Strategy:** Quick verification (already validated in UAT)

```
Setup → Unit Tests → Deploy → Migration → Smoke Tests
```

**No QA tests** - Service was already validated in UAT

**Only Smoke Tests:**
- ✅ Quick health checks
- ✅ Verify deployment succeeded
- ✅ Fast execution (< 1 minute)

---

### Pipeline Flow Example

#### UAT Workflow (Complete)

```yaml
workflows:
  faas-offer-uat:
    jobs:
      # Phase 1: Setup and Unit Tests
      - base-orb/setup:
          name: Setup
      
      - base-orb/python_pytest:
          name: Pytest  # Service unit tests
          requires: [Setup]
      
      # Phase 2: Deployment
      - base-orb/setup_deploy:
          requires: [Pytest]
          name: Deploy setup - UAT
      
      - base-orb/terraform_init:
          requires: [Deploy setup - UAT]
          name: Terraform Init and Plan - UAT
      
      - hold-tf:
          type: approval
          requires: [Terraform Init and Plan - UAT]
      
      - base-orb/terraform_apply:
          requires: [hold-tf]
          name: Terraform Apply - UAT
      
      - base-orb/migration:
          requires: [Terraform Apply - UAT]
          name: Run Migration - UAT
      
      # Phase 3: Centralized QA Tests (AFTER deployment)
      - qa-trigger/run_service_tests:
          name: QA Integration Tests
          service: offer
          test_suite: integration
          environment: uat
          requires: [Run Migration - UAT]
          context: [faas-qa-secrets]
      
      - qa-trigger/run_service_e2e:
          name: QA E2E Tests
          service: offer
          environment: uat
          requires: [QA Financial Tests]
          context: [faas-qa-secrets]
      
      # Phase 4: Post-Deploy Validation
      - qa-trigger/run_smoke_tests:
          name: Post-Deploy Smoke Tests
          service: offer
          environment: uat
          requires: [QA E2E Tests]
          context: [faas-qa-secrets]
      
      # Phase 5: Promotion Gate
      - hold-promotion:
          type: approval
          requires: [Post-Deploy Smoke Tests]
      
      - base-orb/promotion:
          deploy_environment: UAT
          requires: [hold-promotion]
```

---

## Examples

### Example 1: Adding QA to `faas_offer` Service

**Before:**
```yaml
# faas_offer/.circleci/config.yml
workflows:
  faas-offer-uat:
    jobs:
      - base-orb/setup
      - base-orb/python_pytest
      - base-orb/terraform_apply
      - base-orb/migration
      - hold-promotion
```

**After:**
```yaml
# faas_offer/.circleci/config.yml
orbs:
  base-orb: retail-capital/ci-base@6
  qa-trigger: retail-capital/qa-automation@1  # Added

workflows:
  faas-offer-uat:
    jobs:
      - base-orb/setup
      - base-orb/python_pytest
      - base-orb/terraform_apply
      - base-orb/migration
      
      # Added QA tests
      - qa-trigger/run_service_tests:
          name: QA Integration Tests
          service: offer
          environment: uat
          requires: [Run Migration - UAT]
          context: [faas-qa-secrets]
      
      - qa-trigger/run_service_e2e:
          name: QA E2E Tests
          service: offer
          environment: uat
          requires: [QA Financial Tests]
          context: [faas-qa-secrets]
      
      - qa-trigger/run_smoke_tests:
          name: Post-Deploy Smoke Tests
          service: offer
          environment: uat
          requires: [QA E2E Tests]
          context: [faas-qa-secrets]
      
      - hold-promotion:
          requires: [Post-Deploy Smoke Tests]
```

---

### Example 2: Complete Journey Test (ATM Partner)

```typescript
// tests/journeys/test_atm_journey.spec.ts
import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'https://uat.api.rcdevops.co.za';
const PARTNER_ID = '5e9d531c-791b-463a-aeea-233eb7d04a9b'; // ATM

test.describe('ATM Partner Journey', () => {
  test('should complete full ATM partner journey', async ({ request, page }) => {
    // Step 1: Get partner config
    const configResponse = await request.get(
      `${BASE_URL}/partner/${PARTNER_ID}/config`,
      { headers: { 'Authorization': `Bearer ${process.env.AUTH_TOKEN}` } }
    );
    const config = await configResponse.json();
    const offerUrl = config.offerConfig.url; // e.g., "atm.com"
    
    // Step 2: Get offer
    const offersResponse = await request.get(
      `${BASE_URL}/offer/${PARTNER_ID}/offers?page=1&pageSize=1`,
      { headers: { 'Authorization': `Bearer ${process.env.AUTH_TOKEN}` } }
    );
    const offers = await offersResponse.json();
    const offerId = offers[0][0].id;
    
    // Step 3: Frontend validation
    await page.goto(`${offerUrl}/offer?offerID=${offerId}`);
    await expect(page.locator('.partner-logo')).toBeVisible();
    await expect(page.locator('.slider')).toBeVisible();
    
    // Step 4: Complete onboarding (3 screens)
    await completeOnboarding(page);
    
    // Step 5: Contract creation
    const contract = await waitForContract(offerId);
    
    // Step 6: CRM verification
    await verifyCRMSubmission(contract.id);
    
    // Step 7: Test activation
    await activateContract(contract.id, {
      invoiceNumber: 'TEST-INV-001',
      crmNumber: 'TEST-CRM-001'
    });
    
    // Step 8: Sage integration
    await verifySageIntegration(contract.id);
    
    // Step 9: Partner API integration
    await verifyPartnerNotification(PARTNER_ID, contract.id);
  });
});
```

---

### Example 3: Service Test Structure

```
tests/services/offer/
├── integration/
│   ├── __init__.py
│   ├── test_api_endpoints.py      # All API endpoints
│   ├── test_calculations.py       # Financial calculations
│   └── test_validation.py         # Input validation
│
└── e2e/
    ├── __init__.py
    └── test_offer_journey.py      # Complete offer validation flow
                                    # (get offer → validate → get validation result)
```

---

## Summary

### Key Takeaways

1. **Centralized Approach**
   - QA team owns all tests
   - Tests live in central repository
   - Services trigger via CircleCI Orb

2. **Comprehensive Testing**
   - Integration: API contract validation
   - E2E: Internal service journeys
   - Journey: Partner-specific complete flows
   - Regression: Orchestrates all journeys
   - Smoke: Quick health checks

3. **Environment Strategy**
   - Development: Fast feedback, unit tests only
   - UAT: Full QA validation after deployment
   - Production: Smoke tests only

4. **Partner Journeys**
   - One test file per partner
   - Covers all tiers: onboarding, CRM, Sage, partner API
   - Frontend validation with Playwright
   - Complete end-to-end verification

5. **Easy Integration**
   - Add orb to service CircleCI config
   - Add QA test jobs to workflow
   - Set up CircleCI context
   - Notify QA team to add tests

### Benefits

✅ **Specialization** - QA team becomes experts  
✅ **Consistency** - Uniform approach across services  
✅ **Independence** - Tests independent of service code  
✅ **Comprehensive** - All tiers covered in journey tests  
✅ **Scalable** - Easy to add new services and partners  
✅ **Maintainable** - Centralized test maintenance  

---

## Next Steps

1. **For Service Teams:**
   - Add QA orb to CircleCI config
   - Add QA test jobs to workflows
   - Set up CircleCI context
   - Contact QA team for test creation

2. **For QA Team:**
   - Create tests for new services
   - Add partner journey tests
   - Maintain and update test suite
   - Monitor test results

3. **For Platform:**
   - Expand journey tests to all partners
   - Add performance tests
   - Enhance reporting dashboard
   - Optimize test execution

---

**This centralized QA automation strategy provides comprehensive, scalable, and maintainable testing for the entire FAAS platform.**
