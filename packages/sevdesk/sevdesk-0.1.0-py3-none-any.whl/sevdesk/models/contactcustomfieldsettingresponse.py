from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.sevclient import SevClient

class ContactCustomFieldSettingResponse(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    sevClient: Optional[SevClient] = None
    name: Optional[str] = None
    identifier: Optional[str] = None
    description: Optional[str] = None
    class Config:
        populate_by_name = True