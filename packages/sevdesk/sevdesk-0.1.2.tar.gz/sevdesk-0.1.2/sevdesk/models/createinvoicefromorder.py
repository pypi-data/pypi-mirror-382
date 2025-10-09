from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.order import Order

class CreateInvoiceFromOrder(BaseModel):
    order: Order
    type_: Optional[str] = Field(default=None, alias="type")
    amount: Optional[float] = None
    partialType: Optional[str] = None
    class Config:
        populate_by_name = True