# Partner Journey Tests

## Overview

Partner journey tests are comprehensive end-to-end tests that verify the complete flow for each partner. Each journey covers all tiers of integration:

1. **Onboarding** (3 screens)
2. **CRM Integration** (Salesforce verification)
3. **Sage Integration** (Financial system sync)
4. **Partner External API Integration** (Partner notification)

## Journey Flow

Each partner journey follows this flow:

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

## Partner-Specific Tests

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
- `test_payfast_journey.spec.ts` - PayFast partner journey

## Running Journey Tests

### Run All Journeys
```bash
npx playwright test tests/journeys/
```

### Run Specific Partner Journey
```bash
npx playwright test tests/journeys/test_atm_journey.spec.ts
```

### Run Tier 1 Partner Journeys Only
```bash
pytest tests/regression/test_tier1_services.py::TestTier1Regression::test_tier1_partner_journeys
```

## Environment Variables

Required environment variables:

- `BASE_URL` - Base API URL (default: `https://uat.api.rcdevops.co.za`)
- `AUTH_TOKEN` - Authentication token
- `TEST_INVOICE_NUMBER` - Test invoice number for activation (optional)
- `TEST_CRM_NUMBER` - Test CRM number for activation (optional)

## Partner IDs

Partner IDs are defined in each journey test file:

- ATM: `5e9d531c-791b-463a-aeea-233eb7d04a9b`
- FNB: `82c1c0a8-a203-4a73-8750-cf2dfe21835d`
- NetCash: `30f50c8b-7b88-49c1-8b61-ca93b8f6ea7e`
- Tabbs: `960f7a46-180d-4615-a87a-31e0dbeb1b64`
- Kazang: `1d51ef18-0d07-403b-a499-3fd2296532ef`
- iKhokha: `675911fa-95ad-4fdd-adea-802240c79887`
- Takealot: `e01c1138-d4c3-4b5d-8ca2-ea1034b91f9e`
- PayFast: `c7b09cd3-a52f-468b-93a7-3c438036a50c`
- Korridor: `449703d7-913d-4798-aa28-05adfe7e1ef5`

## Integration with Regression Tests

Regression tests simply orchestrate running all partner journeys:

```python
# tests/regression/test_tier1_services.py
def test_all_partner_journeys(self):
    """Run all partner journey tests"""
    # Executes: npx playwright test tests/journeys/
```

This means:
- **Service deployment** → Runs service QA tests → Runs regression → Runs all journeys
- Each journey covers all tiers (onboarding, CRM, Sage, partner API)
- No separate regression test suite needed - journeys are comprehensive
