from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.invoice import Invoice
from sevdesk.converters.part import Part
from sevdesk.converters.unity import Unity
from sevdesk.converters.sevclient import SevClient

class InvoicePos(BaseModel):
    id_: Optional[int] = Field(default=None, alias="id")
    objectName: str
    mapAll: bool
    create: Optional[str] = None
    update: Optional[str] = None
    invoice: Optional[Invoice] = None
    part: Optional[Part] = None
    quantity: float
    price: Optional[float] = None
    name: Optional[str] = None
    unity: Unity
    sevClient: Optional[SevClient] = None
    positionNumber: Optional[int] = None
    text: Optional[str] = None
    discount: Optional[float] = None
    taxRate: float
    sumDiscount: Optional[float] = None
    sumNetAccounting: Optional[float] = None
    sumTaxAccounting: Optional[float] = None
    sumGrossAccounting: Optional[float] = None
    priceNet: Optional[float] = None
    priceGross: Optional[float] = None
    priceTax: Optional[float] = None
    class Config:
        populate_by_name = True