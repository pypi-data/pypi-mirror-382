from typing import Optional
from pydantic import BaseModel, Field


class ContactCustomFieldSettingUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    objectName: Optional[str] = None
    class Config:
        populate_by_name = True