from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.invoice import Invoice
from sevdesk.converters.part import Part
from sevdesk.converters.unity import Unity
from sevdesk.converters.sevclient import SevClient

class InvoicePosResponse(BaseModel):
    id_: Optional[str] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    invoice: Optional[Invoice] = None
    part: Optional[Part] = None
    quantity: Optional[bool] = None
    price: Optional[str] = None
    name: Optional[str] = None
    unity: Optional[Unity] = None
    sevClient: Optional[SevClient] = None
    positionNumber: Optional[str] = None
    text: Optional[str] = None
    discount: Optional[str] = None
    taxRate: Optional[str] = None
    sumDiscount: Optional[str] = None
    sumNetAccounting: Optional[str] = None
    sumTaxAccounting: Optional[str] = None
    sumGrossAccounting: Optional[str] = None
    priceNet: Optional[str] = None
    priceGross: Optional[str] = None
    priceTax: Optional[str] = None
    class Config:
        populate_by_name = True