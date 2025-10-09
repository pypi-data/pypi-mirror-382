from typing import Optional
from pydantic import BaseModel, Field


class CheckAccountUpdate(BaseModel):
    name: Optional[str] = None
    type_: Optional[str] = Field(default=None, alias="type")
    importType: Optional[str] = None
    currency: Optional[str] = None
    defaultAccount: Optional[int] = None
    status: Optional[int] = None
    autoMapTransactions: Optional[int] = None
    accountingNumber: Optional[str] = None
    class Config:
        populate_by_name = True