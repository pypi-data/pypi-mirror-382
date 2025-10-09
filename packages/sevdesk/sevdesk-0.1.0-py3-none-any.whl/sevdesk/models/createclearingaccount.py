from typing import Optional
from pydantic import BaseModel, Field


class CreateClearingAccount(BaseModel):
    name: Optional[str] = None
    accountingNumber: Optional[int] = None
    class Config:
        populate_by_name = True