from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.category import Category
from sevdesk.converters.unity import Unity
from sevdesk.converters.sevclient import SevClient

class PartUpdate(BaseModel):
    id_: Optional[int] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    name: Optional[str] = None
    partNumber: Optional[str] = None
    text: Optional[str] = None
    category: Optional[Category] = None
    stock: Optional[float] = None
    stockEnabled: Optional[bool] = None
    unity: Optional[Unity] = None
    price: Optional[float] = None
    priceNet: Optional[float] = None
    priceGross: Optional[float] = None
    sevClient: Optional[SevClient] = None
    pricePurchase: Optional[float] = None
    taxRate: Optional[float] = None
    status: Optional[int] = None
    internalComment: Optional[str] = None
    class Config:
        populate_by_name = True