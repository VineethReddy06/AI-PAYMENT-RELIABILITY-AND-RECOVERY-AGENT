from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    amount: float = Field(gt=0)
    payment_method: str
    bank: str
    gateway: str