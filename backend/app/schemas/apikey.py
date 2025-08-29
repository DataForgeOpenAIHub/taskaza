from datetime import datetime
from pydantic import BaseModel


class APIKeyOut(BaseModel):
    id: int
    prefix: str
    created_at: datetime
    revoked: bool

    class Config:
        orm_mode = True


class APIKeyCreated(APIKeyOut):
    key: str
