from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.checkaccount import CheckAccount
from sevdesk.converters.sourcetransaction import SourceTransaction
from sevdesk.converters.targettransaction import TargetTransaction

class CheckAccountTransactionUpdate(BaseModel):
    valueDate: Optional[str] = None
    entryDate: Optional[str] = None
    paymtPurpose: Optional[str] = None
    amount: Optional[float] = None
    payeePayerName: Optional[str] = None
    checkAccount: Optional[CheckAccount] = None
    status: Optional[int] = None
    sourceTransaction: Optional[SourceTransaction] = None
    targetTransaction: Optional[TargetTransaction] = None
    class Config:
        populate_by_name = True