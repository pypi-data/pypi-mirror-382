from unittest import TestCase
from glpi_provider.utils.url import url_transform


class UrlTransformTestCase(TestCase):

    def test_url_transform(self):
        received_data = 'https://192.168.0.1/'
        expected_data = 'https://192.168.0.1'
        url = url_transform(received_data)
        self.assertEqual(url, expected_data)