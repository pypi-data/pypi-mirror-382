from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.tag import Tag
from sevdesk.converters.object_ import Object_
from sevdesk.converters.sevclient import SevClient

class TagCreateResponse(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    additionalInformation: Optional[str] = None
    create: Optional[str] = None
    tag: Optional[Tag] = None
    object_: Optional[Object_] = Field(default=None, alias="object")
    sevClient: Optional[SevClient] = None
    class Config:
        populate_by_name = True