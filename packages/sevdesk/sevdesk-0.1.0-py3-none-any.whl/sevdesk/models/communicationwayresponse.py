from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.contact import Contact
from sevdesk.converters.key import Key
from sevdesk.converters.sevclient import SevClient

class CommunicationWayResponse(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    contact: Optional[Contact] = None
    type_: Optional[str] = Field(default=None, alias="type")
    value: Optional[str] = None
    key: Optional[Key] = None
    main: Optional[str] = None
    sevClient: Optional[SevClient] = None
    class Config:
        populate_by_name = True