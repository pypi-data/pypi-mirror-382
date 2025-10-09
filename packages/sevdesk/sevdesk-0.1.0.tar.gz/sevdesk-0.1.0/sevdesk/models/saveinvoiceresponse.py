from typing import Optional, Any
from pydantic import BaseModel, Field


class SaveInvoiceResponse(BaseModel):
    invoice: Optional[str] = None
    invoicePos: Optional[Any] = None
    filename: Optional[str] = None
    class Config:
        populate_by_name = True