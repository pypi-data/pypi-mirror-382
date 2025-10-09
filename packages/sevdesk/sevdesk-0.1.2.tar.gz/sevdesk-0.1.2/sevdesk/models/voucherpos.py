from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.sevclient import SevClient
from sevdesk.converters.voucher import Voucher
from sevdesk.converters.accountdatev import AccountDatev
from sevdesk.converters.accountingtype import AccountingType
from sevdesk.converters.estimatedaccountingtype import EstimatedAccountingType

class VoucherPos(BaseModel):
    id_: Optional[int] = Field(default=None, alias="id")
    objectName: str
    mapAll: bool
    create: Optional[str] = None
    update: Optional[str] = None
    sevClient: Optional[SevClient] = None
    voucher: Voucher
    accountDatev: AccountDatev
    accountingType: AccountingType
    estimatedAccountingType: Optional[EstimatedAccountingType] = None
    taxRate: float
    net: bool
    isAsset: Optional[bool] = None
    sumNet: float
    sumTax: Optional[float] = None
    sumGross: float
    sumNetAccounting: Optional[float] = None
    sumTaxAccounting: Optional[float] = None
    sumGrossAccounting: Optional[float] = None
    comment: Optional[str] = None
    class Config:
        populate_by_name = True