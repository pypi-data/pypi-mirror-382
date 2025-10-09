from pydantic import BaseModel, Field


class ChangeLayout(BaseModel):
    key: str
    value: str
    class Config:
        populate_by_name = True