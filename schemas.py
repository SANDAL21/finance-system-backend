from pydantic import BaseModel, Field
from typing import Literal

class TransactionCreate (BaseModel):
    amount: float = Field(gt=0)
    type: Literal["income", "expense"]
    category :str
    date: str
    description: str