from pydantic import BaseModel


class VerificationToken(BaseModel):
    token: str


class Message(BaseModel):
    detail: str
