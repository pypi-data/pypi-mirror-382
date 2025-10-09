from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.sevclient import SevClient

class TagResponse(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    additionalInformation: Optional[str] = None
    create: Optional[str] = None
    name: Optional[str] = None
    sevClient: Optional[SevClient] = None
    class Config:
        populate_by_name = True