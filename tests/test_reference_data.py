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

    def test_homepage_labels_nfirs_as_legacy_and_neris_as_current(self):
        homepage = (ROOT / 'templates/index.html').read_text()
        self.assertIn('calendar-year 2026 incident reporting is exclusively in NERIS', homepage)
        self.assertIn('NFIRS Draft Demonstration', homepage)
        self.assertIn('Legacy', homepage)
        self.assertNotIn('NFIRS Assistant <span class="pill live">', homepage)
        self.assertNotIn('Volunteer depts lose ~50%', homepage)
        self.assertNotIn('Multiple studies', homepage)

    def test_deploy_workflow_tracks_reference_data(self):
        workflow = (ROOT / '.github/workflows/deploy.yml').read_text()
        self.assertIn("- 'tools_data.py'", workflow)


if __name__ == '__main__':
    unittest.main()
