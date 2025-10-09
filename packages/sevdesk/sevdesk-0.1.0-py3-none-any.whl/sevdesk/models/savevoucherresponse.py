from typing import Optional, Any
from pydantic import BaseModel, Field


class SaveVoucherResponse(BaseModel):
    voucher: Optional[str] = None
    voucherPos: Optional[Any] = None
    filename: Optional[str] = None
    class Config:
        populate_by_name = True