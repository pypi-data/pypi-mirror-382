from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.parent import Parent
from sevdesk.converters.category import Category
from sevdesk.converters.sevclient import SevClient

class ContactResponse(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None
    customerNumber: Optional[str] = None
    parent: Optional[Parent] = None
    surename: Optional[str] = None
    familyname: Optional[str] = None
    titel: Optional[str] = None
    category: Optional[Category] = None
    description: Optional[str] = None
    academicTitle: Optional[str] = None
    gender: Optional[str] = None
    sevClient: Optional[SevClient] = None
    name2: Optional[str] = None
    birthday: Optional[str] = None
    vatNumber: Optional[str] = None
    bankAccount: Optional[str] = None
    bankNumber: Optional[str] = None
    defaultCashbackTime: Optional[str] = None
    defaultCashbackPercent: Optional[str] = None
    defaultTimeToPay: Optional[str] = None
    taxNumber: Optional[str] = None
    taxOffice: Optional[str] = None
    exemptVat: Optional[str] = None
    defaultDiscountAmount: Optional[str] = None
    defaultDiscountPercentage: Optional[str] = None
    buyerReference: Optional[str] = None
    governmentAgency: Optional[str] = None
    additionalInformation: Optional[str] = None
    class Config:
        populate_by_name = True