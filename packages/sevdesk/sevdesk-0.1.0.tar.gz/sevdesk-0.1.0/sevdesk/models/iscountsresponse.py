from typing import Optional
from pydantic import BaseModel, Field


class IscountsResponse(BaseModel):
    id_: Optional[int] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    sevClient: Optional[str] = None
    discount: Optional[str] = None
    text: Optional[str] = None
    percentage: Optional[str] = None
    value: Optional[str] = None
    isNet: Optional[str] = None
    class Config:
        populate_by_name = True