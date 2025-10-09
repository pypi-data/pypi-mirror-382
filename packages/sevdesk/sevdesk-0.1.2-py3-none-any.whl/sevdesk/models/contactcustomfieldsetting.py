from typing import Optional
from pydantic import BaseModel, Field


class ContactCustomFieldSetting(BaseModel):
    name: str
    description: Optional[str] = None
    objectName: Optional[str] = None
    class Config:
        populate_by_name = True