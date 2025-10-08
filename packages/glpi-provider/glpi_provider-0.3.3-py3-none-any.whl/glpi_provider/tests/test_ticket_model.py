from datetime import datetime
from unittest import TestCase
from glpi_provider.models import Entity, Ticket


class TicketTestCase(TestCase):

    def test_ticket_instance(self): 
        entity_data = {
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
        entity = Entity(**entity_data)
        ticket_data = {
            'id': 13123,
            'entity': entity,
            'content': '&lt;p&gt;***** RECORRENTE****&lt;/p&gt;&lt;p&gt;\xa0&lt;/p&gt;&lt;p&gt;FAVOR VERIFICAR QUEDA DE LIGAÇÕES (ESTE É O TERCEIRO CHAMADO ABERTO PELO MOTIVO)&lt;/p&gt;', 
            'date_creation': '2024-10-21 15:31:46', 
            'user': None
        }
        ticket = Ticket(**ticket_data)
        self.assertEqual(ticket.id, 13123)
        self.assertEqual(ticket.entity, entity)
        self.assertEqual(ticket.content, '&lt;p&gt;***** RECORRENTE****&lt;/p&gt;&lt;p&gt;\xa0&lt;/p&gt;&lt;p&gt;FAVOR VERIFICAR QUEDA DE LIGAÇÕES (ESTE É O TERCEIRO CHAMADO ABERTO PELO MOTIVO)&lt;/p&gt;')
        self.assertEqual(ticket.date_creation, datetime.strptime('2024-10-21 15:31:46', '%Y-%m-%d %H:%M:%S'))