from unittest import TestCase
from glpi_provider.models import Location


class LocationTestCase(TestCase):

    def test_location_model(self):
        location = Location(id=8, name="Location Test")
        self.assertEqual(location.id, 8)
        self.assertEqual(location.name, "Location Test")
