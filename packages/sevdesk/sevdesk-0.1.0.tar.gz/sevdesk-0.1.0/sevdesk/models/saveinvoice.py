from typing import Optional, Any
from pydantic import BaseModel, Field

from sevdesk.converters.discountdelete import DiscountDelete

class SaveInvoice(BaseModel):
    invoice: str
    invoicePosSave: Optional[Any] = None
    invoicePosDelete: Optional[str] = None
    filename: Optional[str] = None
    discountSave: Optional[Any] = None
    discountDelete: Optional[DiscountDelete] = None
    class Config:
        populate_by_name = True