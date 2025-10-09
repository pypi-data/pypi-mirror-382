from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.object_ import Object_

class Discount(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    object_: Optional[Object_] = Field(default=None, alias="object")
    sevClient: Optional[str] = None
    text: Optional[str] = None
    percentage: Optional[str] = None
    value: Optional[str] = None
    isNet: Optional[str] = None
    class Config:
        populate_by_name = True