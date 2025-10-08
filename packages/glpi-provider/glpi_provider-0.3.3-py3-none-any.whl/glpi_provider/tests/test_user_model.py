from unittest import TestCase
from glpi_provider.models import User


class UserTestCase(TestCase):

    def test_user_instance(self):
        received_data = {
            "id": 8,
            "last_name": "Alves",
            "first_name": "Tatianno",
            "mobile": "+5511997799778"
        }
        user = User(**received_data)
        self.assertEqual(user.id, 8)
        self.assertEqual(user.full_name, 'Tatianno Alves')
        self.assertEqual(user.mobile, '+5511997799778')