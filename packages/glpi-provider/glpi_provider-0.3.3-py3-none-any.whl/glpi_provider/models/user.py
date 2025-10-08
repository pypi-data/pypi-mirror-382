from dataclasses import dataclass
from typing import Optional
from .location import Location


@dataclass
class User:
    id: int
    last_name: str
    first_name: str
    mobile: Optional[str] = None
    username: Optional[str] = None
    location: Optional[Location] = None    
    _location_id: Optional[int] = None

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'