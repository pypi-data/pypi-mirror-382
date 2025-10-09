from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.sevclient import SevClient

class EmailOrder(BaseModel):
    id_: Optional[int] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    object_: Optional[str] = Field(default=None, alias="object")
    from_: str = Field(alias="from")
    to_: str = Field(alias="to")
    subject: str
    text: Optional[str] = None
    sevClient: Optional[SevClient] = None
    cc: Optional[str] = None
    bcc: Optional[str] = None
    arrived: Optional[str] = None
    class Config:
        populate_by_name = True