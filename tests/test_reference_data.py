import unittest
from pathlib import Path

from tools_data import SOURCE_RETRIEVED, TOOLS


ROOT = Path(__file__).resolve().parents[1]


class ReferenceDataTests(unittest.TestCase):
    def test_technical_tools_expose_dated_primary_sources(self):
        self.assertEqual(SOURCE_RETRIEVED, '2026-07-16')
        for slug in ('training-tracker', 'pre-incident', 'sog-search'):
            with self.subTest(tool=slug):
                self.assertTrue(TOOLS[slug].get('authorities'))
                for source in TOOLS[slug]['authorities']:
                    self.assertTrue(source['url'].startswith('https://'))
                    self.assertEqual(source['retrieved'], SOURCE_RETRIEVED)
                    self.assertTrue(source['version'])

    def test_training_prompt_uses_current_nfpa_families(self):
        tool = TOOLS['training-tracker']
        prompt = tool['system_prompt']
        self.assertIn('NFPA 1010', tool['tagline'] + prompt)
        self.assertIn('NFPA 1020', prompt)
        self.assertIn('NFPA 1006', prompt)
        self.assertIn('Do not treat the 2027 edition as in force', prompt)
        self.assertIn('formally adopted by the state/AHJ', tool['authorities'][2]['version'])
        self.assertIn('superseded standalone NFPA 1001, 1002, 1021, or 1041', prompt)
        self.assertIn('Verify the exact edition', prompt)

    def test_preincident_prompt_does_not_invent_site_or_tactics(self):
        tool = TOOLS['pre-incident']
        prompt = tool['system_prompt']
        self.assertIn('NFPA 1660', tool['tagline'])
        self.assertIn('UNKNOWN / VERIFY ON SITE', prompt)
        self.assertIn('never assume a location or fixed distance', prompt)
        self.assertIn('Do not recommend alarm assignments', prompt)
        for unsafe in (
            'hydrant locations within 300 ft',
            'with assumed locations',
            'RECOMMENDED RESPONSE',
            'initial alarm assignment for this occupancy',
        ):
            self.assertNotIn(unsafe, prompt)

    def test_sog_prompt_uses_current_nfpa_and_osha_sources(self):
        prompt = TOOLS['sog-search']['system_prompt']
        self.assertIn('NFPA 1550 (2024)', prompt)
        self.assertIn('OSHA 29 CFR 1910.134', prompt)
        self.assertIn('Never treat this output as real-time scene direction', prompt)

    def test_homepage_holds_neris_claims_pending_source_review(self):
        homepage = (ROOT / 'templates/index.html').read_text(encoding='utf-8')
        self.assertIn('Official-source review in progress', homepage)
        self.assertIn('does not currently assert transition dates or reporting status', homepage)
        self.assertIn('NERIS Preparation Assistant', homepage)
        self.assertIn('No official codes', homepage)
        self.assertIn('Review hold', homepage)
        self.assertNotIn('href="https://nfirs.freshskyai.com"', homepage)
        self.assertNotIn('NFIRS Draft Demonstration', homepage)
        self.assertNotIn('NFIRS Assistant <span class="pill live">', homepage)
        self.assertNotIn('Volunteer depts lose ~50%', homepage)
        self.assertNotIn('Multiple studies', homepage)
        self.assertNotIn('without charging departments', homepage)
        self.assertNotIn('The code is yours', homepage)
        self.assertNotIn('work for any department out of the box', homepage)
        self.assertIn('do not promise development', homepage)
        self.assertIn('clearly displayed monthly Civic price', homepage)
        self.assertNotIn('HULEC', homepage)
        self.assertNotIn('halal', homepage.lower())

    def test_deploy_workflow_is_manual_and_deploys_repository_source(self):
        workflow = (ROOT / '.github/workflows/deploy.yml').read_text()
        self.assertIn('workflow_dispatch:', workflow)
        self.assertNotIn('push:', workflow)
        self.assertIn('--source .', workflow)
        self.assertIn('--no-traffic', workflow)
        self.assertIn('--tag="$CANDIDATE_TAG"', workflow)
        self.assertIn('CANDIDATE_TAG="candidate-${GITHUB_SHA:0:12}"', workflow)
        self.assertIn('stripe-runtime-restricted-key:latest', workflow)
        self.assertNotIn('STRIPE_SECRET_KEY=stripe-secret-key:latest', workflow)
        self.assertIn('Stable production traffic changed', workflow)
        self.assertIn('Production traffic promotion: not performed', workflow)


if __name__ == '__main__':
    unittest.main()
