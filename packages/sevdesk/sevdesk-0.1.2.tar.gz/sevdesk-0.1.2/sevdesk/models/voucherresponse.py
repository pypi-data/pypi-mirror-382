from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.sevclient import SevClient
from sevdesk.converters.createuser import CreateUser
from sevdesk.converters.supplier import Supplier
from sevdesk.converters.document import Document
from sevdesk.converters.taxrule import TaxRule
from sevdesk.converters.costcentre import CostCentre
from sevdesk.converters.taxset import TaxSet

class VoucherResponse(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    mapAll: Optional[bool] = None
    create: Optional[str] = None
    update: Optional[str] = None
    sevClient: Optional[SevClient] = None
    createUser: Optional[CreateUser] = None
    voucherDate: Optional[str] = None
    supplier: Optional[Supplier] = None
    supplierName: Optional[str] = None
    description: Optional[str] = None
    document: Optional[Document] = None
    payDate: Optional[str] = None
    status: Optional[str] = None
    sumNet: Optional[str] = None
    sumTax: Optional[str] = None
    sumGross: Optional[str] = None
    sumNetAccounting: Optional[str] = None
    sumTaxAccounting: Optional[str] = None
    sumGrossAccounting: Optional[str] = None
    sumDiscounts: Optional[str] = None
    sumDiscountsForeignCurrency: Optional[str] = None
    paidAmount: Optional[float] = None
    taxRule: Optional[TaxRule] = None
    taxType: Optional[str] = None
    creditDebit: Optional[str] = None
    costCentre: Optional[CostCentre] = None
    voucherType: Optional[str] = None
    currency: Optional[str] = None
    propertyForeignCurrencyDeadline: Optional[str] = None
    propertyExchangeRate: Optional[str] = None
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
    class Config:
        populate_by_name = True