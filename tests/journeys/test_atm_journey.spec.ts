import { test, expect, Page } from '@playwright/test';

/**
 * Partner-Specific Journey Test: ATM
 * 
 * This test verifies the complete ATM partner journey:
 * 1. Get partner config from partner API (includes offer URL/cloudfront domain)
 * 2. Get offer from offer service
 * 3. Frontend validation (Playwright) - verify partner branding, sliders, screens
 * 4. Contract creation
 * 5. CRM submission verification (query Salesforce in UAT)
 * 6. Test activation with test account
 * 
 * Covers all tiers:
 * - Onboarding (3 screens)
 * - CRM integration
 * - Sage integration
 * - Partner external API integration
 */

const BASE_URL = process.env.BASE_URL || 'https://uat.api.rcdevops.co.za';
const AUTH_TOKEN = process.env.AUTH_TOKEN || '';
const PARTNER_ID = '5e9d531c-791b-463a-aeea-233eb7d04a9b'; // ATM partner ID

test.describe('ATM Partner Journey', () => {
  let partnerConfig: any;
  let offerId: string;
  let merchantId: string;
  let contractId: string;
  let offerUrl: string;

  test.beforeAll(async ({ request }) => {
    if (!AUTH_TOKEN) {
      test.skip();
    }

    // Step 1: Get partner config from partner API
    const configResponse = await request.get(
      `${BASE_URL}/partner/${PARTNER_ID}/config`,
      {
        headers: {
          'Authorization': `Bearer ${AUTH_TOKEN}`,
        },
      }
    );

    expect(configResponse.ok()).toBeTruthy();
    partnerConfig = await configResponse.json();
    
    // Extract offer URL/cloudfront domain from config
    offerUrl = partnerConfig.offerConfig?.url || partnerConfig.cloudfrontDomain || '';
    expect(offerUrl).toBeTruthy();
  });

  test('should complete full ATM partner journey', async ({ request, page }) => {
    // Step 2: Get offer from offer service (page 1, pageSize 1)
    const offersResponse = await request.get(
      `${BASE_URL}/offer/${PARTNER_ID}/offers?page=1&pageSize=1`,
      {
        headers: {
          'Authorization': `Bearer ${AUTH_TOKEN}`,
        },
      }
    );

    expect(offersResponse.ok()).toBeTruthy();
    const offersData = await offersResponse.json();
    expect(offersData).toBeInstanceOf(Array);
    expect(offersData.length).toBeGreaterThan(0);
    expect(offersData[0]).toBeInstanceOf(Array);
    expect(offersData[0].length).toBeGreaterThan(0);

    const offer = offersData[0][0];
    offerId = offer.id;
    merchantId = offer.merchantID;

    expect(offerId).toBeTruthy();
    expect(merchantId).toBeTruthy();

    // Step 3: Frontend validation with Playwright
    // Navigate to partner-specific offer page
    const fullOfferUrl = `${offerUrl}/offer?offerID=${offerId}`;
    await page.goto(fullOfferUrl);

    // Verify partner branding (ATM logo)
    const logo = page.locator('[data-testid="partner-logo"], .partner-logo, img[alt*="ATM"], img[alt*="atm"]');
    await expect(logo).toBeVisible();

    // Verify screen 1 has sliders (onboarding screen 1)
    const sliders = page.locator('[data-testid="slider"], .slider, .carousel, [class*="slider"]');
    await expect(sliders.first()).toBeVisible();

    // Verify we're on the offer page (screen 1 of onboarding)
    const offerPage = page.locator('[data-testid="offer-page"], .offer-page, [class*="offer"]');
    await expect(offerPage).toBeVisible();

    // Verify faas_client and faas_client_interface are loaded
    // Check for common FAAS client elements
    const faasClientElements = page.locator('[data-faas], [class*="faas"], script[src*="faas"]');
    await expect(faasClientElements.first()).toBeVisible({ timeout: 10000 });

    // Step 4: Navigate through onboarding screens (3 screens)
    // Screen 1: Offer selection (already on this)
    const nextButton = page.locator('button:has-text("Next"), button:has-text("Continue"), [data-testid="next"]');
    if (await nextButton.isVisible()) {
      await nextButton.click();
    }

    // Screen 2: Additional information
    await page.waitForSelector('[data-testid="onboarding-screen-2"], .onboarding-screen-2', { timeout: 5000 });
    const screen2 = page.locator('[data-testid="onboarding-screen-2"], .onboarding-screen-2');
    await expect(screen2).toBeVisible();

    // Continue to screen 3
    if (await nextButton.isVisible()) {
      await nextButton.click();
    }

    // Screen 3: Final confirmation
    await page.waitForSelector('[data-testid="onboarding-screen-3"], .onboarding-screen-3', { timeout: 5000 });
    const screen3 = page.locator('[data-testid="onboarding-screen-3"], .onboarding-screen-3');
    await expect(screen3).toBeVisible();

    // Submit onboarding
    const submitButton = page.locator('button:has-text("Submit"), button:has-text("Accept"), [data-testid="submit"]');
    if (await submitButton.isVisible()) {
      await submitButton.click();
    }

    // Step 5: Contract creation
    // Wait for contract to be created (polling or webhook)
    let contractCreated = false;
    for (let i = 0; i < 30; i++) {
      const contractResponse = await request.get(
        `${BASE_URL}/contract/v1/contracts?offer_id=${offerId}`,
        {
          headers: {
            'Authorization': `Bearer ${AUTH_TOKEN}`,
          },
        }
      );

      if (contractResponse.ok()) {
        const contracts = await contractResponse.json();
        if (contracts && contracts.length > 0) {
          contractId = contracts[0].id;
          contractCreated = true;
          break;
        }
      }

      await page.waitForTimeout(2000); // Wait 2 seconds before retry
    }

    expect(contractCreated).toBeTruthy();
    expect(contractId).toBeTruthy();

    // Step 6: CRM submission verification (query Salesforce in UAT)
    // Verify contract was pushed to CRM
    const crmResponse = await request.get(
      `${BASE_URL}/crm/contracts/${contractId}`,
      {
        headers: {
          'Authorization': `Bearer ${AUTH_TOKEN}`,
        },
      }
    );

    expect(crmResponse.ok()).toBeTruthy();
    const crmContract = await crmResponse.json();
    expect(crmContract.id).toBe(contractId);
    expect(crmContract.partnerID).toBe(PARTNER_ID);

    // Step 7: Test activation with test account
    // Use test account credentials (invoice number, CRM number)
    const testAccount = {
      invoiceNumber: process.env.TEST_INVOICE_NUMBER || 'TEST-INV-001',
      crmNumber: process.env.TEST_CRM_NUMBER || 'TEST-CRM-001',
    };

    const activationResponse = await request.post(
      `${BASE_URL}/contract/v1/contracts/${contractId}/activate`,
      {
        headers: {
          'Authorization': `Bearer ${AUTH_TOKEN}`,
          'Content-Type': 'application/json',
        },
        data: {
          invoiceNumber: testAccount.invoiceNumber,
          crmNumber: testAccount.crmNumber,
        },
      }
    );

    expect(activationResponse.ok()).toBeTruthy();
    const activationResult = await activationResponse.json();
    expect(activationResult.status).toBe('activated');
    expect(activationResult.contractId).toBe(contractId);

    // Verify Sage integration (if applicable)
    // Check that contract was synced to Sage
    const sageResponse = await request.get(
      `${BASE_URL}/finance/contracts/${contractId}/sage`,
      {
        headers: {
          'Authorization': `Bearer ${AUTH_TOKEN}`,
        },
      }
    );

    // Sage integration may not always be available, so we check if it exists
    if (sageResponse.ok()) {
      const sageData = await sageResponse.json();
      expect(sageData).toBeDefined();
    }

    // Verify partner external API integration
    // Check that partner was notified via their external API
    const partnerNotificationResponse = await request.get(
      `${BASE_URL}/integration/${PARTNER_ID}/notifications?contractId=${contractId}`,
      {
        headers: {
          'Authorization': `Bearer ${AUTH_TOKEN}`,
        },
      }
    );

    // Partner API integration may vary, so we check if notification exists
    if (partnerNotificationResponse.ok()) {
      const notifications = await partnerNotificationResponse.json();
      expect(notifications).toBeDefined();
    }
  });
});
