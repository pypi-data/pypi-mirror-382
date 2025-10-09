from typing import Optional
from pydantic import BaseModel, Field


class Export_Progress_Data(BaseModel):
    current: Optional[int] = None
    total: Optional[int] = None
    class Config:
        populate_by_name = True