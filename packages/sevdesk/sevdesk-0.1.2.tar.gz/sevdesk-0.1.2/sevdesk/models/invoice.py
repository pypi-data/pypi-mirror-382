from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.contact import Contact
from sevdesk.converters.contactperson import ContactPerson
from sevdesk.converters.sevclient import SevClient
from sevdesk.converters.addresscountry import AddressCountry
from sevdesk.converters.createuser import CreateUser
from sevdesk.converters.taxrule import TaxRule
from sevdesk.converters.taxset import TaxSet
from sevdesk.converters.paymentmethod import PaymentMethod
from sevdesk.converters.origin import Origin

class Invoice(BaseModel):
    id_: Optional[int] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    invoiceNumber: Optional[str] = None
    contact: Contact
    contactPerson: ContactPerson
    create: Optional[str] = None
    update: Optional[str] = None
    sevClient: Optional[SevClient] = None
    invoiceDate: str
    header: Optional[str] = None
    headText: Optional[str] = None
    footText: Optional[str] = None
    timeToPay: Optional[int] = None
    discount: int
    address: Optional[str] = None
    addressCountry: AddressCountry
    payDate: Optional[str] = None
    createUser: Optional[CreateUser] = None
    deliveryDate: Optional[str] = None
    deliveryDateUntil: Optional[int] = None
    status: str
    smallSettlement: Optional[bool] = None
    taxRate: float
    taxRule: TaxRule
    taxText: str
    taxType: str
    taxSet: Optional[TaxSet] = None
    dunningLevel: Optional[int] = None
    paymentMethod: Optional[PaymentMethod] = None
    sendDate: Optional[str] = None
    invoiceType: str
    accountIntervall: Optional[str] = None
    accountNextInvoice: Optional[int] = None
    currency: str
    sumNet: Optional[float] = None
    sumTax: Optional[float] = None
    sumGross: Optional[float] = None
    sumDiscounts: Optional[float] = None
    sumNetForeignCurrency: Optional[float] = None
    sumTaxForeignCurrency: Optional[float] = None
    sumGrossForeignCurrency: Optional[float] = None
    sumDiscountsForeignCurrency: Optional[float] = None
    sumNetAccounting: Optional[float] = None
    sumTaxAccounting: Optional[float] = None
    sumGrossAccounting: Optional[float] = None
    paidAmount: Optional[float] = None
    showNet: Optional[bool] = None
    enshrined: Optional[str] = None
    sendType: Optional[str] = None
    origin: Optional[Origin] = None
    customerInternalNote: Optional[str] = None
    propertyIsEInvoice: Optional[bool] = None
    mapAll: bool
    class Config:
        populate_by_name = True