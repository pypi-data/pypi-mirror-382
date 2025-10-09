from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.order import Order
from sevdesk.converters.part import Part
from sevdesk.converters.unity import Unity
from sevdesk.converters.sevclient import SevClient

class OrderPos(BaseModel):
    id_: Optional[int] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    order: Optional[Order] = None
    part: Optional[Part] = None
    quantity: float
    price: Optional[float] = None
    priceNet: Optional[float] = None
    priceTax: Optional[float] = None
    priceGross: Optional[float] = None
    name: Optional[str] = None
    unity: Unity
    sevClient: Optional[SevClient] = None
    positionNumber: Optional[int] = None
    text: Optional[str] = None
    discount: Optional[float] = None
    optional: Optional[bool] = None
    taxRate: float
    sumDiscount: Optional[float] = None
    class Config:
        populate_by_name = True