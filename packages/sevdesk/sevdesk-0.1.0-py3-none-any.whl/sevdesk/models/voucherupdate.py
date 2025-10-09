from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.supplier import Supplier
from sevdesk.converters.taxrule import TaxRule
from sevdesk.converters.taxset import TaxSet
from sevdesk.converters.document import Document
from sevdesk.converters.costcentre import CostCentre

class VoucherUpdate(BaseModel):
    voucherDate: Optional[str] = None
    supplier: Optional[Supplier] = None
    supplierName: Optional[str] = None
    description: Optional[str] = None
    payDate: Optional[str] = None
    status: Optional[float] = None
    paidAmount: Optional[float] = None
    taxRule: Optional[TaxRule] = None
    taxType: Optional[str] = None
    creditDebit: Optional[str] = None
    voucherType: Optional[str] = None
    currency: Optional[str] = None
    propertyForeignCurrencyDeadline: Optional[str] = None
    propertyExchangeRate: Optional[float] = None
    taxSet: Optional[TaxSet] = None
    paymentDeadline: Optional[str] = None
    deliveryDate: Optional[str] = None
    deliveryDateUntil: Optional[str] = None
    document: Optional[Document] = None
    costCentre: Optional[CostCentre] = None
    class Config:
        populate_by_name = True