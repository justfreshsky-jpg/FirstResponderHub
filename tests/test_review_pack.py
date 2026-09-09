import unittest

from app import app


class ReviewPackRouteTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_review_pack_is_free_local_and_deidentified(self):
        response = self.client.get('/review-pack')
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn('uploads nothing', text)
        self.assertIn('requires no sign-in', text)
        self.assertIn('Do not enter PII, PHI', text)
        self.assertIn('does not establish operational readiness', text)
        self.assertNotIn('checkout', text.lower())

    def test_sitemap_includes_review_pack(self):
        response = self.client.get('/sitemap.xml')
        self.assertIn('/review-pack</loc>', response.get_data(as_text=True))

    def test_shared_access_bundle_uses_neutral_public_copy(self):
        response = self.client.get('/freshsky-access-v062.js')
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertNotIn('halal', text.lower())
        self.assertIn('HULEC operating standard', text)


if __name__ == '__main__':
    unittest.main()
