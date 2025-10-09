from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.sevclient import SevClient
from sevdesk.converters.voucher import Voucher
from sevdesk.converters.accountdatev import AccountDatev
from sevdesk.converters.accountingtype import AccountingType
from sevdesk.converters.estimatedaccountingtype import EstimatedAccountingType

class VoucherPosResponse(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    sevClient: Optional[SevClient] = None
    voucher: Voucher
    accountDatev: AccountDatev
    accountingType: AccountingType
    estimatedAccountingType: Optional[EstimatedAccountingType] = None
    taxRate: str
    net: bool
    isAsset: Optional[bool] = None
    sumNet: str
    sumTax: Optional[str] = None
    sumGross: str
    sumNetAccounting: Optional[str] = None
    sumTaxAccounting: Optional[str] = None
    sumGrossAccounting: Optional[str] = None
    comment: Optional[str] = None
    class Config:
        populate_by_name = True