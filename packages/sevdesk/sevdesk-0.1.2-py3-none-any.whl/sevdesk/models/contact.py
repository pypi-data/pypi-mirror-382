from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.parent import Parent
from sevdesk.converters.category import Category

class Contact(BaseModel):
    name: Optional[str] = None
    status: Optional[int] = None
    customerNumber: Optional[str] = None
    parent: Optional[Parent] = None
    surename: Optional[str] = None
    familyname: Optional[str] = None
    titel: Optional[str] = None
    category: Category
    description: Optional[str] = None
    academicTitle: Optional[str] = None
    gender: Optional[str] = None
    name2: Optional[str] = None
    birthday: Optional[str] = None
    vatNumber: Optional[str] = None
    bankAccount: Optional[str] = None
    bankNumber: Optional[str] = None
    defaultCashbackTime: Optional[int] = None
    defaultCashbackPercent: Optional[float] = None
    defaultTimeToPay: Optional[int] = None
    taxNumber: Optional[str] = None
    taxOffice: Optional[str] = None
    exemptVat: Optional[bool] = None
    defaultDiscountAmount: Optional[float] = None
    defaultDiscountPercentage: Optional[bool] = None
    buyerReference: Optional[str] = None
    governmentAgency: Optional[bool] = None
    class Config:
        populate_by_name = True