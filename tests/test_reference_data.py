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

    def test_homepage_labels_neris_as_current_and_nfirs_as_retired(self):
        homepage = (ROOT / 'templates/index.html').read_text()
        self.assertIn('NFIRS is decommissioned; NERIS is current', homepage)
        self.assertIn('calendar-year 2026 incident reporting is exclusively in NERIS', homepage)
        self.assertIn('NERIS Preparation Assistant', homepage)
        self.assertIn('No official codes', homepage)
        self.assertNotIn('NFIRS Draft Demonstration', homepage)
        self.assertNotIn('NFIRS Assistant <span class="pill live">', homepage)
        self.assertNotIn('Volunteer depts lose ~50%', homepage)
        self.assertNotIn('Multiple studies', homepage)

    def test_civic_access_and_sensitive_data_boundaries_are_explicit(self):
        homepage = (ROOT / 'templates/index.html').read_text()
        tools_index = (ROOT / 'templates/tools_index.html').read_text()
        tools_run = (ROOT / 'templates/tools_run.html').read_text()
        app_source = (ROOT / 'app.py').read_text()
        requirements = (ROOT / 'requirements.txt').read_text()
        workflow = (ROOT / '.github/workflows/deploy.yml').read_text()

        for page in (homepage, tools_index):
            self.assertIn('$14.99/month', page)
            self.assertIn('40 usage units per day', page)
            self.assertIn('200 per month', page)
            self.assertIn('Civic', page)
        for page in (homepage, tools_index, tools_run):
            self.assertIn('rosters', page)
            self.assertIn('CAPIDs', page)
            self.assertIn('PHI', page)
            self.assertIn('incident or case identifiers', page)
            self.assertIn('operational secrets', page)
        self.assertNotIn('Advanced $29.99/month', homepage)
        self.assertIn("subscription_tier='civic'", app_source)
        self.assertIn("workspace_id='civic'", app_source)
        self.assertIn(
            '56282af02bd9b6a85774e3b1b3caec221bb2ed2b',
            requirements,
        )
        self.assertIn('FRESHSKY_WORKSPACE_ID=civic', workflow)

    def test_deploy_workflow_tracks_reference_data(self):
        workflow = (ROOT / '.github/workflows/deploy.yml').read_text()
        self.assertIn("- 'tools_data.py'", workflow)


if __name__ == '__main__':
    unittest.main()
