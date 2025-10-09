from pydantic import BaseModel, Field

from sevdesk.converters.contact import Contact
from sevdesk.converters.contactcustomfieldsetting import ContactCustomFieldSetting

class ContactCustomField(BaseModel):
    contact: Contact
    contactCustomFieldSetting: ContactCustomFieldSetting
    value: str
    objectName: str
    class Config:
        populate_by_name = True