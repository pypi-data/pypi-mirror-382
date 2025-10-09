from typing import Optional, Any
from pydantic import BaseModel, Field


class ReceiptGuideDto(BaseModel):
    accountDatevId: Optional[int] = None
    accountNumber: Optional[str] = None
    accountName: Optional[str] = None
    description: Optional[str] = None
    allowedTaxRules: Optional[Any] = None
    allowedReceiptTypes: Optional[Any] = None
    class Config:
        populate_by_name = True