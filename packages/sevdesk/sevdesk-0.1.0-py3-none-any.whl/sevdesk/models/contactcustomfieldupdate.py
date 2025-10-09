from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.contact import Contact
from sevdesk.converters.contactcustomfieldsetting import ContactCustomFieldSetting

class ContactCustomFieldUpdate(BaseModel):
    contact: Optional[Contact] = None
    contactCustomFieldSetting: Optional[ContactCustomFieldSetting] = None
    value: Optional[str] = None
    objectName: Optional[str] = None
    class Config:
        populate_by_name = True