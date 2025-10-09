from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.contact import Contact
from sevdesk.converters.addresscountry import AddressCountry
from sevdesk.converters.createuser import CreateUser
from sevdesk.converters.sevclient import SevClient
from sevdesk.converters.contactperson import ContactPerson
from sevdesk.converters.taxrule import TaxRule
from sevdesk.converters.taxset import TaxSet

class CreditNoteUpdate(BaseModel):
    id_: Optional[int] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    creditNoteNumber: Optional[str] = None
    contact: Optional[Contact] = None
    creditNoteDate: Optional[str] = None
    status: Optional[str] = None
    header: Optional[str] = None
    headText: Optional[str] = None
    footText: Optional[str] = None
    addressCountry: Optional[AddressCountry] = None
    createUser: Optional[CreateUser] = None
    sevClient: Optional[SevClient] = None
    deliveryDate: Optional[str] = None
    smallSettlement: Optional[bool] = None
    contactPerson: Optional[ContactPerson] = None
    taxRate: Optional[float] = None
    taxRule: Optional[TaxRule] = None
    taxSet: Optional[TaxSet] = None
    taxText: Optional[str] = None
    taxType: Optional[str] = None
    sendDate: Optional[str] = None
    address: Optional[str] = None
    currency: Optional[str] = None
    sumNet: Optional[float] = None
    sumTax: Optional[float] = None
    sumGross: Optional[float] = None
    sumDiscounts: Optional[float] = None
    sumNetForeignCurrency: Optional[float] = None
    sumTaxForeignCurrency: Optional[float] = None
    sumGrossForeignCurrency: Optional[float] = None
    sumDiscountsForeignCurrency: Optional[float] = None
    customerInternalNote: Optional[str] = None
    showNet: Optional[bool] = None
    sendType: Optional[str] = None
    class Config:
        populate_by_name = True