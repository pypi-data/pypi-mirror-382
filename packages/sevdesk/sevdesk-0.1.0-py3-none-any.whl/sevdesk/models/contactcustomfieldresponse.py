from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.sevclient import SevClient
from sevdesk.converters.contact import Contact

class ContactCustomFieldResponse(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    sevClient: Optional[SevClient] = None
    contact: Optional[Contact] = None
    contactCustomFieldSetting: Optional[dict] = None
    value: Optional[str] = None
    class Config:
        populate_by_name = True