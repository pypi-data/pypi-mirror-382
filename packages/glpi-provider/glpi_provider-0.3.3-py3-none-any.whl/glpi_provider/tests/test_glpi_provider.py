from unittest import TestCase
from unittest.mock import MagicMock
from glpi_provider.models import Entity, Location, Ticket, User
from glpi_provider.providers.glpi_provider import GlpiProvider
from glpi_provider.tests.constants.entities_responses import (
    ENTITY_RESPONSE, 
    ENTITIES_RESPONSE
)
from glpi_provider.tests.constants.locations_responses import (
    LOCATION_RESPONSE,
    LOCATION_SEARCH_RESPONSE,
    LOCATIONS_SEARCH_RESPONSE
)
from glpi_provider.tests.constants.tickets_responses import (
    TICKET_REPONSE, 
    TICKETS_RESPONSE, 
    TICKET_OPEN_RESPONSE
)
from glpi_provider.tests.constants.users_responses import (
    USER_RESPONSE, 
    USERS_RESPONSE,
    USER_SEARCH_RESPONSE,
    USERS_SEARCH_RESPONSE
)


class GlpiProviderTestCase(TestCase):

    def test_get_user(self):
        service = MagicMock()
        service.get_user.return_value = USER_RESPONSE
        provider = GlpiProvider(service)
        user = provider.get_user(user_id=8)
        self.assertEqual(type(user), User)
    
    def test_get_users(self):
        service = MagicMock()
        service.get_users.return_value = USERS_RESPONSE
        provider = GlpiProvider(service)
        users = provider.get_users()
        self.assertEqual(len(users), 16)
    
    def test_find_user_by_username(self):
        service = MagicMock()
        service.find_user_by_username.return_value = USERS_SEARCH_RESPONSE
        service.get_user.return_value = USER_RESPONSE
        provider = GlpiProvider(service)
        user = provider.find_user_by_username('aramaral')
        self.assertEqual(type(user), User)
    
    def test_find_user_by_username_not_case_sensitive(self):
        service = MagicMock()
        service.find_user_by_username.return_value = USERS_SEARCH_RESPONSE
        service.get_user.return_value = USER_RESPONSE
        provider = GlpiProvider(service)
        user = provider.find_user_by_username('Aramaral')
        self.assertEqual(type(user), User)
    
    def test_find_user_by_username_not_found(self):
        service = MagicMock()
        service.find_user_by_username.return_value = USERS_SEARCH_RESPONSE
        service.get_user.return_value = USER_RESPONSE
        provider = GlpiProvider(service)
        user = provider.find_user_by_username('teste')
        self.assertIsNone(user)

    def test_parser_user_data(self):
        expected_data = {
            "id": 8,
            "last_name": "Alves",
            "first_name": "Tatianno",
            "mobile": "",
            "username": 'tatianno',
            "_location_id": None
        }
        service = MagicMock()
        provider = GlpiProvider(service)
        user_data = provider._parser_user_data(USER_RESPONSE)
        self.assertDictEqual(user_data, expected_data)
    
    def test_parser_search_user_data(self):
        expected_data = {
            'id': 8,
            'last_name': 'Alves',
            'first_name': 'Tatianno',
            'username': 'aramaral'
        }
        service = MagicMock()
        provider = GlpiProvider(service)
        user_data = provider._parser_search_user_data(USER_SEARCH_RESPONSE)
        self.assertDictEqual(user_data, expected_data)
    
    def test_get_entity(self):
        service = MagicMock()
        service.get_entity.return_value = ENTITY_RESPONSE
        provider = GlpiProvider(service)
        entity = provider.get_entity(entity_id=8)
        self.assertEqual(type(entity), Entity)
    
    def test_get_entities(self):
        service = MagicMock()
        service.get_entities.return_value = ENTITIES_RESPONSE
        provider = GlpiProvider(service)
        entities = provider.get_entities()
        self.assertEqual(len(entities), 16)

    def test_parser_entity_data(self):
        expected_data = {
            'id': 6, 
            'name': 'XXXXXXXX - DESENTUPIDORA LTDA - EPP', 
            'address': 'R MARIA XDXXXXXXXXXX, 15\r\nJD OSASCO', 
            'postcode': 'XXXXXXXX', 
            'town': 'OSASCO', 
            'state': 'SP', 
            'country': 'BRASIL', 
            'phonenumber': '11 XXXXXXXXXX', 
            'admin_email': 'tatianno.alves@gnew.com.br', 
            'admin_email_name': 'Tatianno'
        }
        service = MagicMock()
        provider = GlpiProvider(service)
        entity_data = provider._parser_entity_data(ENTITY_RESPONSE)
        self.assertDictEqual(entity_data, expected_data)
    
    def test_get_ticket(self):
        service = MagicMock()
        service.get_ticket.return_value = TICKET_REPONSE
        service.get_entity.return_value = ENTITY_RESPONSE
        provider = GlpiProvider(service)
        ticket = provider.get_ticket(ticket_id=8)
        self.assertEqual(type(ticket), Ticket)
    
    def test_get_tickets(self):
        service = MagicMock()
        service.get_tickets.return_value = TICKETS_RESPONSE
        service.get_entity.return_value = ENTITY_RESPONSE
        provider = GlpiProvider(service)
        tickets = provider.get_tickets()
        self.assertEqual(len(tickets), 16)

    def test_parser_entity_data(self):
        expected_data = {'id': 6, 'content': None, 'date_creation': '2019-03-23 11:15:14'}
        service = MagicMock()
        provider = GlpiProvider(service)
        ticket_data, entity_id = provider._parser_ticket_data(ENTITY_RESPONSE)
        self.assertDictEqual(ticket_data, expected_data)
        self.assertEqual(entity_id, 0)

    def test_parser_open_ticket_data(self):
        expected_data = {
            'id': 12835,
            'content': "VERIFICAR CONSISTENCIAS DE UMA CONSULTA PASSADA PELO CLIENTE. CONTATO:",
            'owner_id': 8,
            'status_id': 4,
            'entity': "GNEW > CASTIQUINI & OLIVEIRA LTDA - ME > UNIMED PRESIDENTE PRUDENTE"
        }
        service = MagicMock()
        provider = GlpiProvider(service)
        ticket_data = provider._parser_open_ticket_data(TICKET_OPEN_RESPONSE)
        self.assertDictEqual(ticket_data, expected_data)
    
    def test_find_location_by_name(self):
        service = MagicMock()
        service.find_location_by_name.return_value = LOCATIONS_SEARCH_RESPONSE
        provider = GlpiProvider(service)
        locations = provider.find_location_by_name("ativa")
        self.assertEqual(len(locations), 4)
    
    def test_get_location(self):
        service = MagicMock()
        service.get_location.return_value = LOCATION_RESPONSE
        provider = GlpiProvider(service)
        location = provider.get_location(id=1)
        self.assertEqual(type(location), Location)
        
    def test_create_location(self):
        service = MagicMock()
        provider = GlpiProvider(service)
        location_data = provider._parser_location_data(LOCATION_SEARCH_RESPONSE)
        location = provider._create_location(location_data)
        self.assertEqual(type(location), Location)
    
    def test_parse_location_data(self):
        expected_data = {
            'id': 36,
            'name': 'CPRACES - Câmara de prevenção e resolução administrativa de conflitos do ES - 7º andar'
        }
        service = MagicMock()
        provider = GlpiProvider(service)
        location_data = provider._parser_location_data(LOCATION_SEARCH_RESPONSE)
        self.assertDictEqual(location_data, expected_data)
    
    