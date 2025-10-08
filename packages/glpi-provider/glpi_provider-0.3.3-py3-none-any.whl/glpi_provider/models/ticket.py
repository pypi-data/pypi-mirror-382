from datetime import datetime
from dataclasses import dataclass
from .entity import Entity
from .user import User


@dataclass
class Ticket: 
    id: int
    entity: Entity
    content: str
    user: User
    date_creation: datetime

    def __post_init__(self):
        self.date_creation = datetime.strptime(self.date_creation, '%Y-%m-%d %H:%M:%S')