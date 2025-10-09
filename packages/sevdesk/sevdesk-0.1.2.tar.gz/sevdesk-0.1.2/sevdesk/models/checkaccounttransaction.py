from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.sevclient import SevClient
from sevdesk.converters.checkaccount import CheckAccount
from sevdesk.converters.sourcetransaction import SourceTransaction
from sevdesk.converters.targettransaction import TargetTransaction

class CheckAccountTransaction(BaseModel):
    id_: Optional[int] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    sevClient: Optional[SevClient] = None
    valueDate: str
    entryDate: Optional[str] = None
    paymtPurpose: Optional[str] = None
    amount: float
    payeePayerName: Optional[str]
    payeePayerAcctNo: Optional[str] = None
    payeePayerBankCode: Optional[str] = None
    checkAccount: CheckAccount
    status: int
    sourceTransaction: Optional[SourceTransaction] = None
    targetTransaction: Optional[TargetTransaction] = None
    class Config:
        populate_by_name = True