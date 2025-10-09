from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.contact import Contact
from sevdesk.converters.country import Country
from sevdesk.converters.category import Category
from sevdesk.converters.sevclient import SevClient

class ContactAddress(BaseModel):
    id_: Optional[int] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    contact: Contact
    street: Optional[str] = None
    zip: Optional[str] = None
    city: Optional[str] = None
    country: Country
    category: Optional[Category]
    name: Optional[str] = None
    sevClient: Optional[SevClient] = None
    name2: Optional[str] = None
    name3: Optional[str] = None
    name4: Optional[str] = None
    class Config:
        populate_by_name = True