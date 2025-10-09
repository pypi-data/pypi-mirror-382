from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.contact import Contact
from sevdesk.converters.country import Country
from sevdesk.converters.category import Category

class ContactAddressUpdate(BaseModel):
    contact: Optional[Contact] = None
    street: Optional[str] = None
    zip: Optional[str] = None
    city: Optional[str] = None
    country: Optional[Country] = None
    category: Optional[Category] = None
    name: Optional[str] = None
    name2: Optional[str] = None
    name3: Optional[str] = None
    name4: Optional[str] = None
    class Config:
        populate_by_name = True