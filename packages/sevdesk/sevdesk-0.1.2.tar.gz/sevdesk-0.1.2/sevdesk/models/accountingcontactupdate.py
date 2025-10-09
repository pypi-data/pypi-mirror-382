from typing import Optional
from pydantic import BaseModel, Field

from sevdesk.converters.contact import Contact

class AccountingContactUpdate(BaseModel):
    contact: Optional[Contact] = None
    debitorNumber: Optional[int] = None
    creditorNumber: Optional[int] = None
    class Config:
        populate_by_name = True