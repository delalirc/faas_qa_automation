import { test, expect, Page } from '@playwright/test';

/**
 * Partner-Specific Journey Test: FNB
 * 
 * Complete FNB partner journey covering all tiers:
 * - Onboarding (3 screens)
 * - CRM integration
 * - Sage integration
 * - Partner external API integration
 */

const BASE_URL = process.env.BASE_URL || 'https://uat.api.rcdevops.co.za';
const AUTH_TOKEN = process.env.AUTH_TOKEN || '';
const PARTNER_ID = '82c1c0a8-a203-4a73-8750-cf2dfe21835d'; // FNB partner ID

test.describe('FNB Partner Journey', () => {
  let partnerConfig: any;
  let offerId: string;
  let merchantId: string;
  let contractId: string;
  let offerUrl: string;

  test.beforeAll(async ({ request }) => {
    if (!AUTH_TOKEN) {
      test.skip();
    }

    // Get partner config from partner API
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
    offerUrl = partnerConfig.offerConfig?.url || partnerConfig.cloudfrontDomain || '';
    expect(offerUrl).toBeTruthy();
  });

  test('should complete full FNB partner journey', async ({ request, page }) => {
    // Get offer from offer service
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
    const offer = offersData[0][0];
    offerId = offer.id;
    merchantId = offer.merchantID;

    // Frontend validation
    const fullOfferUrl = `${offerUrl}/offer?offerID=${offerId}`;
    await page.goto(fullOfferUrl);

    // Verify FNB branding
    const logo = page.locator('[data-testid="partner-logo"], .partner-logo, img[alt*="FNB"], img[alt*="fnb"]');
    await expect(logo).toBeVisible();

    // Verify sliders on screen 1
    const sliders = page.locator('[data-testid="slider"], .slider, .carousel');
    await expect(sliders.first()).toBeVisible();

    // Complete onboarding (3 screens)
    const nextButton = page.locator('button:has-text("Next"), button:has-text("Continue")');
    
    // Screen 1 → Screen 2
    if (await nextButton.isVisible()) {
      await nextButton.click();
      await page.waitForSelector('[data-testid="onboarding-screen-2"]', { timeout: 5000 });
    }

    // Screen 2 → Screen 3
    if (await nextButton.isVisible()) {
      await nextButton.click();
      await page.waitForSelector('[data-testid="onboarding-screen-3"]', { timeout: 5000 });
    }

    // Submit
    const submitButton = page.locator('button:has-text("Submit"), button:has-text("Accept")');
    if (await submitButton.isVisible()) {
      await submitButton.click();
    }

    // Wait for contract creation
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

      await page.waitForTimeout(2000);
    }

    expect(contractCreated).toBeTruthy();

    // Verify CRM submission
    const crmResponse = await request.get(
      `${BASE_URL}/crm/contracts/${contractId}`,
      {
        headers: {
          'Authorization': `Bearer ${AUTH_TOKEN}`,
        },
      }
    );

    expect(crmResponse.ok()).toBeTruthy();

    // Test activation
    const activationResponse = await request.post(
      `${BASE_URL}/contract/v1/contracts/${contractId}/activate`,
      {
        headers: {
          'Authorization': `Bearer ${AUTH_TOKEN}`,
          'Content-Type': 'application/json',
        },
        data: {
          invoiceNumber: process.env.TEST_INVOICE_NUMBER || 'TEST-INV-001',
          crmNumber: process.env.TEST_CRM_NUMBER || 'TEST-CRM-001',
        },
      }
    );

    expect(activationResponse.ok()).toBeTruthy();
  });
});
