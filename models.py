from pydantic import BaseModel


class PaymentRequest(BaseModel):
    date: str
    amount: str
    description: str
    type: str
    uuid: str
    status: str
    emitter: str
    receiver: str
    detail: str