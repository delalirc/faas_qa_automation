"""
Regression tests for Tier 1 (critical) services

Regression tests simply orchestrate running all partner journeys.
Each journey covers all tiers: onboarding, CRM, Sage, and partner API integration.
"""

import pytest
import subprocess
import os


@pytest.mark.regression
@pytest.mark.tier1
class TestTier1Regression:
    """Regression tests for Tier 1 services - runs all partner journeys"""
    
    def test_all_partner_journeys(self):
        """
        Run all partner journey tests
        
        Journeys cover:
        - Onboarding (3 screens)
        - CRM integration (Salesforce verification)
        - Sage integration
        - Partner external API integration
        """
        # Run all journey tests using Playwright
        journey_tests_dir = os.path.join(
            os.path.dirname(__file__),
            '..',
            'journeys'
        )
        
        # Execute Playwright tests for all partner journeys
        result = subprocess.run(
            [
                'npx', 'playwright', 'test',
                journey_tests_dir,
                '--reporter=list',
            ],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            pytest.fail(f"Journey tests failed:\n{result.stdout}\n{result.stderr}")
    
    def test_tier1_partner_journeys(self):
        """
        Run Tier 1 partner journeys only (critical partners)
        
        Tier 1 partners: ATM, FNB, NetCash
        """
        tier1_partners = [
            'test_atm_journey.spec.ts',
            'test_fnb_journey.spec.ts',
            'test_netcash_journey.spec.ts',
        ]
        
        journey_tests_dir = os.path.join(
            os.path.dirname(__file__),
            '..',
            'journeys'
        )
        
        for partner_test in tier1_partners:
            test_file = os.path.join(journey_tests_dir, partner_test)
            if os.path.exists(test_file):
                result = subprocess.run(
                    [
                        'npx', 'playwright', 'test',
                        test_file,
                        '--reporter=list',
                    ],
                    cwd=os.path.dirname(os.path.dirname(__file__)),
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    pytest.fail(
                        f"Tier 1 journey test {partner_test} failed:\n"
                        f"{result.stdout}\n{result.stderr}"
                    )
