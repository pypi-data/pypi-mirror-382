from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.contact import Contact
from sevdesk.converters.key import Key

class CommunicationWayUpdate(BaseModel):
    contact: Optional[Contact] = None
    type_: Optional[str] = Field(default=None, alias="type")
    value: Optional[str] = None
    key: Optional[Key] = None
    main: Optional[bool] = None
    class Config:
        populate_by_name = True