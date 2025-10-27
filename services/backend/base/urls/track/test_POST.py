from django.test import TestCase
from ninja.testing import TestClient


class TrackTest(TestCase):
    def test_track(self):
        client = TestClient()
        response = client.post('/track', json={'url': 'http://example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {'message': 'URL tracked successfully', 'url': 'http://example.com'},
        )
