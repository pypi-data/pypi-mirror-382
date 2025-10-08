from glpi_provider.models import Entity, Location, Ticket, User
from glpi_provider.services.glpi_service import GlpiService
from glpi_provider.settings import BASE_URL, APP_TOKEN, USER_TOKEN, TICKET_STATUS


class GlpiProviderException(Exception):

    def __init__(self, message: str) -> None:
        self.message = message


class GlpiProvider:

    def __init__(self, service:GlpiService=None) -> None:
        self.service = service if service else GlpiService(
            base_url=BASE_URL, 
            user_token=USER_TOKEN, 
            status_open=TICKET_STATUS,
            app_token=APP_TOKEN
        )
    
    @property
    def session_token(self) -> str:
        return self.service._session_token
    
    @session_token.setter
    def session_token(self, value: str) -> None:
        self.service._session_token = value
    
    def add_comment(self, ticket_id: int, comment: str) -> None:
        self.service.add_comment(ticket_id, comment)

    def find_entity_by_tag_inventory(self, tag: str) -> Entity:
        entities_data = self.service.find_entity_by_tag_inventory(tag).get('data', [])
        if len(entities_data) != 0:
            for entity_data in entities_data:
                parsed_data = self._parser_search_entity_data(entity_data)
                
                if parsed_data.get('tag') == tag:
                    entity = self.get_entity(parsed_data.get('id'))
                    return entity
        
        return None
    
    def find_location_by_name(self, name: str) -> list[Location]:
        locations_data = self.service.find_location_by_name(name)
        return [
            self._create_location(self._parser_location_data(data)) 
            for data in locations_data.get('data', [])
        ]
    
    def find_user_by_username(self, username: str) -> User:
        users_data = self.service.find_user_by_username(username).get('data', [])
        
        if len(users_data) != 0:
            for user_data in users_data:
                parsed_data = self._parser_search_user_data(user_data)
                
                if parsed_data.get('username', ' ').lower() == username.lower():
                    user = self.get_user(parsed_data.get('id'))
                    return user
        
        return None
    
    def get_entity(self, entity_id: int) -> Entity:
        entity_data = self._parser_entity_data(self.service.get_entity(entity_id))
        return self._create_entity(entity_data)
    
    def get_entities(self) -> list[Entity]:
        entities = []

        for data in self.service.get_entities():
            entity_data = self._parser_entity_data(data)
            entities.append(self._create_entity(entity_data))
        
        return entities
    
    def get_location(self, id: int) -> Location:
        location_data = self.service.get_location(id)
        return self._create_location(
            {
                'id': location_data.get('id'),
                'name': location_data.get('name')
            }
        )

    def get_ticket(self, ticket_id: int) -> Ticket:
        ticket_data, entity_id = self._parser_ticket_data(self.service.get_ticket(ticket_id))
        return self._create_ticket(ticket_data, entity_id)
    
    def get_tickets(self) -> list[Ticket]:
        tickets = []

        for data in self.service.get_tickets():
            ticket_data, entity_id = self._parser_ticket_data(data)
            tickets.append(self._create_ticket(ticket_data, entity_id))
        
        return tickets
    
    def get_open_tickets(self) -> list[dict]:
        tickets = []

        for data in self.service.get_open_tickets().get('data', []):
            tickets.append(self._parser_open_ticket_data(data))
        
        return tickets

    def open_ticket(self, name: str, content: str, requester_id: int, entity_id: int, location_id: int=None, group_assign_id: int=0) -> dict:
        data = {
            'name': name,
            'content': content,
            'requester_id': requester_id,
            '_users_id_requester': requester_id,
            '_groups_id_assign': group_assign_id,
            'entities_id': entity_id,
            'locations_id': location_id,
            'type': 2,
            'itilcategories_id': 198,
            'status': 1,
            'solution_template': 0,
            'solutiontypes_id': 0,
            'requesttypes_id': 1,
            'priority': 2,
        }
        return self.service.open_ticket(data)
    
    def get_user(self, user_id: int) -> User:
        user_data = self._parser_user_data(self.service.get_user(user_id))
        return self._create_user(user_data)
    
    def get_users(self) -> list[User]:
        users = []

        for data in self.service.get_users():
            user_data = self._parser_user_data(data)
            users.append(self._create_user(user_data))
        
        return users
    
    def create_session(self) -> None:
        self.service.create_session()

    def close_session(self) -> None:
        self.service.close_session()
    
    def _create_entity(self, entity_data: dict) -> Entity:
        return Entity(**entity_data)
    
    def _create_location(self, location_data: dict) -> Location:
        return Location(**location_data)
    
    def _create_ticket(self, ticket_data: dict, entity_id: int, user_id: int=None) -> Ticket:
        entity = self.get_entity(entity_id)
        user = self.get_user(user_id) if user_id else None
        ticket_data['entity'] = entity
        ticket_data['user'] = user
        return Ticket(**ticket_data)
    
    def _create_user(self, user_data: dict) -> User:
        user = User(**user_data)
        
        if user._location_id:
            user.location = self.get_location(user._location_id)
            
        return user

    def _parser_entity_data(self, data: dict) -> dict:
        self._validate_data_before_parser(data)
        return {
            'id': data.get('id'),
            'name': data.get('name'),
            'address': data.get('address'),
            'postcode': data.get('postcode'),
            'town': data.get('town'),
            'state': data.get('state'),
            'country': data.get('country'),
            'phonenumber': data.get('phonenumber'),
            'admin_email': data.get('admin_email'),
            'admin_email_name': data.get('admin_email_name')
        }

    def _parser_search_entity_data(self, data: dict) -> dict:
        self._validate_data_before_parser(data)
        return {
            'id': data.get('2'),
            'name': data.get('1'),
            'tag': str(data.get('8')),
        }
    
    def _parser_location_data(self, data: dict) -> dict:
        self._validate_data_before_parser(data)
        return {
            'id': data.get('2'),
            'name': data.get('1')
        }
    
    def _parser_ticket_data(self, data: dict) -> tuple[dict, int]:
        self._validate_data_before_parser(data)
        return (
            {
                'id': data.get('id'),
                'content': data.get('content'),
                'date_creation': data.get('date_creation'),
            },
            data.get('entities_id')
        )
    
    def _parser_open_ticket_data(self, data: dict) -> tuple[int, int]:
        self._validate_data_before_parser(data)
        ticket_data = {
            'id': data.get("2"),
            'content': data.get("1"),
            'owner_id': data.get("5"),
            'status_id': data.get("12"),
            'entity': data.get("80")
        }
        return ticket_data
    
    def _parser_user_data(self, data: dict) -> dict:
        self._validate_data_before_parser(data)
        locations_id = data.get('locations_id', 0)
        first_name = data.get('firstname')
        last_name = data.get('realname')
        return {
            'id': data.get('id'),
            'last_name': last_name,
            'first_name': first_name,
            'mobile': data.get('mobile'),
            'username': data.get('name'),
            '_location_id': locations_id if locations_id != 0 else None
        }
    
    def _parser_search_user_data(self, data: dict) -> dict:
        self._validate_data_before_parser(data)
        return {
            'id': data.get('2'),
            'last_name': data.get('34'),
            'first_name': data.get('9'),
            'username': data.get('1')
        }

    def _validate_data_before_parser(self, data: dict) -> None:
        if type(data) != dict:
            raise GlpiProviderException('Parser data error')