from typing import Optional
from pydantic import BaseModel, Field


class Export_Job_Download_Info(BaseModel):
    filename: Optional[str] = None
    link: Optional[str] = None
    linkExpireDate: Optional[str] = None
    class Config:
        populate_by_name = True