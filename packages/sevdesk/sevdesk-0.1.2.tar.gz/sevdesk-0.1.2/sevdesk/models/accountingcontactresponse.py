from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.contact import Contact
from sevdesk.converters.sevclient import SevClient

class AccountingContactResponse(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    contact: Optional[Contact] = None
    sevClient: Optional[SevClient] = None
    debitorNumber: Optional[str] = None
    creditorNumber: Optional[str] = None
    class Config:
        populate_by_name = True