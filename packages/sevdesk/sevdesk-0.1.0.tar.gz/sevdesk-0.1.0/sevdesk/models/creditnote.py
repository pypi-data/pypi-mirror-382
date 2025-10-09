from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.contact import Contact
from sevdesk.converters.addresscountry import AddressCountry
from sevdesk.converters.createuser import CreateUser
from sevdesk.converters.sevclient import SevClient
from sevdesk.converters.contactperson import ContactPerson
from sevdesk.converters.taxrule import TaxRule
from sevdesk.converters.taxset import TaxSet

class CreditNote(BaseModel):
    id_: Optional[int] = Field(default=None, alias="id")
    objectName: str
    mapAll: bool
    create: Optional[str] = None
    update: Optional[str] = None
    creditNoteNumber: str
    contact: Contact
    creditNoteDate: str
    status: str
    header: str
    headText: Optional[str] = None
    footText: Optional[str] = None
    addressCountry: Optional[AddressCountry]
    createUser: Optional[CreateUser] = None
    sevClient: Optional[SevClient] = None
    smallSettlement: Optional[bool] = None
    contactPerson: ContactPerson
    taxRule: TaxRule
    taxRate: float
    taxSet: Optional[TaxSet] = None
    taxText: str
    taxType: str
    sendDate: Optional[str] = None
    address: Optional[str] = None
    bookingCategory: str
    currency: str
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