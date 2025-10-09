from typing import Optional, Any
from pydantic import BaseModel, Field


class SaveVoucher(BaseModel):
    voucher: str
    voucherPosSave: Optional[Any] = None
    voucherPosDelete: Optional[str] = None
    filename: Optional[str] = None
    class Config:
        populate_by_name = True