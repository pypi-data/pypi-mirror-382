from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.sevclient import SevClient

class CreateFileImportAccountResponse(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    sevClient: Optional[SevClient] = None
    name: Optional[str] = None
    iban: Optional[str] = None
    type_: Optional[str] = Field(default=None, alias="type")
    importType: Optional[str] = None
    currency: Optional[str] = None
    defaultAccount: Optional[str] = None
    status: Optional[str] = None
    autoMapTransactions: Optional[str] = None
    accountingNumber: Optional[str] = None
    class Config:
        populate_by_name = True