from unittest import TestCase
from glpi_provider.models import Entity


class EntityTestCase(TestCase):

    def test_entity_instance(self):
        received_data = {
            "id": 6,
            "name": "XXXXXXXX - DESENTUPIDORA LTDA - EPP",
            "address": "R MARIA XDXXXXXXXXXX, 15\r\nJD OSASCO",
            "postcode": 'XXXXXXXX',
            "town": "OSASCO",
            "state": "SP",
            "country": "BRASIL",
            "phonenumber": "11 4321-4321",
            "admin_email": "tatianno.alves@gnew.com.br",
            "admin_email_name": "Tatianno"
        }
        entity = Entity(**received_data)
        self.assertEqual(entity.id, 6)
        self.assertEqual(entity.name, "XXXXXXXX - DESENTUPIDORA LTDA - EPP")
        self.assertEqual(entity.address, "R MARIA XDXXXXXXXXXX, 15\r\nJD OSASCO")
        self.assertEqual(entity.postcode, 'XXXXXXXX')
        self.assertEqual(entity.town, "OSASCO")
        self.assertEqual(entity.state, "SP")
        self.assertEqual(entity.country, "BRASIL")
        self.assertEqual(entity.phonenumber, "11 4321-4321")
        self.assertEqual(entity.admin_email, "tatianno.alves@gnew.com.br")
        self.assertEqual(entity.admin_email_name, "Tatianno")
