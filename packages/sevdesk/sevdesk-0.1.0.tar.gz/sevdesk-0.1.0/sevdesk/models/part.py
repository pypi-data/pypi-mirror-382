from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.category import Category
from sevdesk.converters.unity import Unity
from sevdesk.converters.sevclient import SevClient

class Part(BaseModel):
    id_: Optional[int] = Field(default=None, alias="id")
    objectName: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    name: str
    partNumber: str
    text: Optional[str] = None
    category: Optional[Category] = None
    stock: float
    stockEnabled: Optional[bool] = None
    unity: Unity
    price: Optional[float] = None
    priceNet: Optional[float] = None
    priceGross: Optional[float] = None
    sevClient: Optional[SevClient] = None
    pricePurchase: Optional[float] = None
    taxRate: float
    status: Optional[int] = None
    internalComment: Optional[str] = None
    class Config:
        populate_by_name = True