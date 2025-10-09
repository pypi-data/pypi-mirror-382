from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.contact import Contact
from sevdesk.converters.addresscountry import AddressCountry
from sevdesk.converters.contactperson import ContactPerson
from sevdesk.converters.taxrule import TaxRule
from sevdesk.converters.taxset import TaxSet
from sevdesk.converters.origin import Origin

class Order(BaseModel):
    id_: Optional[int] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    mapAll: bool
    create: Optional[str] = None
    update: Optional[str] = None
    orderNumber: str
    contact: Contact
    orderDate: str
    status: int
    header: str
    headText: Optional[str] = None
    footText: Optional[str] = None
    addressCountry: AddressCountry
    deliveryTerms: Optional[str] = None
    paymentTerms: Optional[str] = None
    version: int
    smallSettlement: Optional[bool] = None
    contactPerson: ContactPerson
    taxRate: float
    taxRule: TaxRule
    taxSet: Optional[TaxSet] = None
    taxText: str
    taxType: str
    orderType: Optional[str] = None
    sendDate: Optional[str] = None
    address: Optional[str] = None
    currency: str
    customerInternalNote: Optional[str] = None
    showNet: Optional[bool] = None
    sendType: Optional[str] = None
    origin: Optional[Origin] = None
    class Config:
        populate_by_name = True