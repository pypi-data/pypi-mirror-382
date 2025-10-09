from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.sevclient import SevClient
from sevdesk.converters.checkaccount import CheckAccount
from sevdesk.converters.sourcetransaction import SourceTransaction
from sevdesk.converters.targettransaction import TargetTransaction

class CheckAccountTransactionResponse(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    sevClient: Optional[SevClient] = None
    valueDate: Optional[str] = None
    entryDate: Optional[str] = None
    paymtPurpose: Optional[str] = None
    amount: Optional[str] = None
    payeePayerName: Optional[str] = None
    payeePayerAcctNo: Optional[str] = None
    payeePayerBankCode: Optional[str] = None
    gvCode: Optional[str] = None
    entryText: Optional[str] = None
    primaNotaNo: Optional[str] = None
    checkAccount: Optional[CheckAccount] = None
    status: Optional[str] = None
    sourceTransaction: Optional[SourceTransaction] = None
    targetTransaction: Optional[TargetTransaction] = None
    enshrined: Optional[str] = None
    class Config:
        populate_by_name = True