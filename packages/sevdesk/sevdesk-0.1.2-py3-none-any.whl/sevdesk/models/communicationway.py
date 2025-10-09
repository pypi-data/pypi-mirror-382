from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.contact import Contact
from sevdesk.converters.key import Key
from sevdesk.converters.sevclient import SevClient

class CommunicationWay(BaseModel):
    id_: Optional[int] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    contact: Optional[Contact] = None
    type_: str = Field(alias="type")
    value: str
    key: Key
    main: Optional[bool] = None
    sevClient: Optional[SevClient] = None
    class Config:
        populate_by_name = True