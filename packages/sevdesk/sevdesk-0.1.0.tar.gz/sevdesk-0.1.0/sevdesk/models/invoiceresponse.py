from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.contact import Contact
from sevdesk.converters.sevclient import SevClient
from sevdesk.converters.addresscountry import AddressCountry
from sevdesk.converters.createuser import CreateUser
from sevdesk.converters.contactperson import ContactPerson
from sevdesk.converters.taxrule import TaxRule
from sevdesk.converters.paymentmethod import PaymentMethod
from sevdesk.converters.costcentre import CostCentre
from sevdesk.converters.origin import Origin
from sevdesk.converters.taxset import TaxSet

class InvoiceResponse(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    invoiceNumber: Optional[str] = None
    contact: Optional[Contact] = None
    create: Optional[str] = None
    update: Optional[str] = None
    sevClient: Optional[SevClient] = None
    invoiceDate: Optional[str] = None
    header: Optional[str] = None
    headText: Optional[str] = None
    footText: Optional[str] = None
    timeToPay: Optional[str] = None
    discountTime: Optional[str] = None
    discount: Optional[str] = None
    addressCountry: Optional[AddressCountry] = None
    payDate: Optional[str] = None
    createUser: Optional[CreateUser] = None
    deliveryDate: Optional[str] = None
    status: Optional[str] = None
    smallSettlement: Optional[bool] = None
    contactPerson: Optional[ContactPerson] = None
    taxRate: Optional[str] = None
    taxRule: Optional[TaxRule] = None
    taxText: Optional[str] = None
    dunningLevel: Optional[str] = None
    taxType: Optional[str] = None
    paymentMethod: Optional[PaymentMethod] = None
    costCentre: Optional[CostCentre] = None
    sendDate: Optional[str] = None
    origin: Optional[Origin] = None
    invoiceType: Optional[str] = None
    accountIntervall: Optional[str] = None
    accountNextInvoice: Optional[str] = None
    reminderTotal: Optional[str] = None
    reminderDebit: Optional[str] = None
    reminderDeadline: Optional[str] = None
    reminderCharge: Optional[str] = None
    taxSet: Optional[TaxSet] = None
    address: Optional[str] = None
    currency: Optional[str] = None
    sumNet: Optional[str] = None
    sumTax: Optional[str] = None
    sumGross: Optional[str] = None
    sumDiscounts: Optional[str] = None
    sumNetForeignCurrency: Optional[str] = None
    sumTaxForeignCurrency: Optional[str] = None
    sumGrossForeignCurrency: Optional[str] = None
    sumDiscountsForeignCurrency: Optional[str] = None
    sumNetAccounting: Optional[str] = None
    sumTaxAccounting: Optional[str] = None
    sumGrossAccounting: Optional[str] = None
    paidAmount: Optional[float] = None
    customerInternalNote: Optional[str] = None
    showNet: Optional[bool] = None
    enshrined: Optional[str] = None
    sendType: Optional[str] = None
    deliveryDateUntil: Optional[str] = None
    datevConnectOnline: Optional[dict] = None
    sendPaymentReceivedNotificationDate: Optional[str] = None
    class Config:
        populate_by_name = True