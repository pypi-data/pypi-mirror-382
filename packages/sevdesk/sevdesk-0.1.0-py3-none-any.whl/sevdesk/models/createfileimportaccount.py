from typing import Optional
from pydantic import BaseModel, Field


class CreateFileImportAccount(BaseModel):
    name: Optional[str] = None
    importType: Optional[str] = None
    accountingNumber: Optional[int] = None
    iban: Optional[str] = None
    class Config:
        populate_by_name = True