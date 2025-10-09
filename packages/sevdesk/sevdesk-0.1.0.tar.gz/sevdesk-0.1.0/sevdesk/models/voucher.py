from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.sevclient import SevClient
from sevdesk.converters.createuser import CreateUser
from sevdesk.converters.supplier import Supplier
from sevdesk.converters.taxrule import TaxRule
from sevdesk.converters.taxset import TaxSet
from sevdesk.converters.document import Document
from sevdesk.converters.costcentre import CostCentre

class Voucher(BaseModel):
    id_: Optional[int] = Field(default=None, alias="id")
    objectName: str
    mapAll: bool
    create: Optional[str] = None
    update: Optional[str] = None
    sevClient: Optional[SevClient] = None
    createUser: Optional[CreateUser] = None
    voucherDate: Optional[str] = None
    supplier: Optional[Supplier] = None
    supplierName: Optional[str] = None
    description: Optional[str] = None
    payDate: Optional[str] = None
    status: float
    sumNet: Optional[float] = None
    sumTax: Optional[float] = None
    sumGross: Optional[float] = None
    sumNetAccounting: Optional[float] = None
    sumTaxAccounting: Optional[float] = None
    sumGrossAccounting: Optional[float] = None
    sumDiscounts: Optional[float] = None
    sumDiscountsForeignCurrency: Optional[float] = None
    paidAmount: Optional[float] = None
    taxRule: TaxRule
    taxType: str
    creditDebit: str
    voucherType: str
    currency: Optional[str] = None
    propertyForeignCurrencyDeadline: Optional[str] = None
    propertyExchangeRate: Optional[float] = None
    recurringInterval: Optional[str] = None
    recurringStartDate: Optional[str] = None
    recurringNextVoucher: Optional[str] = None
    recurringLastVoucher: Optional[str] = None
    recurringEndDate: Optional[str] = None
    enshrined: Optional[str] = None
    taxSet: Optional[TaxSet] = None
    paymentDeadline: Optional[str] = None
    deliveryDate: Optional[str] = None
    deliveryDateUntil: Optional[str] = None
    document: Optional[Document] = None
    costCentre: Optional[CostCentre] = None
    class Config:
        populate_by_name = True