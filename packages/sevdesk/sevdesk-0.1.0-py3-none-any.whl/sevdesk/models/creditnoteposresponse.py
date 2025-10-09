from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.creditnote import CreditNote
from sevdesk.converters.part import Part
from sevdesk.converters.unity import Unity
from sevdesk.converters.sevclient import SevClient

class CreditNotePosResponse(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    creditNote: CreditNote
    part: Optional[Part] = None
    quantity: str
    price: Optional[str] = None
    priceNet: Optional[str] = None
    priceTax: Optional[str] = None
    priceGross: Optional[str] = None
    name: Optional[str] = None
    unity: Unity
    sevClient: Optional[SevClient] = None
    positionNumber: Optional[str] = None
    text: Optional[str] = None
    discount: Optional[str] = None
    optional: Optional[bool] = None
    taxRate: str
    sumDiscount: Optional[str] = None
    class Config:
        populate_by_name = True