from dataclasses import dataclass


@dataclass
class Entity: 
    id: int
    name: str
    address: str
    postcode: str
    town: str
    state: str
    country: str
    phonenumber: str
    admin_email: str
    admin_email_name: str