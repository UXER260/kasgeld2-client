# client/models.py
# bevat alle pydantic models
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class UserLoginField(BaseModel):
    email_address: str
    password: str


class UserSignupField(BaseModel):
    name: str
    email_address: str
    password: str
    saldo: float
    update_kasgeld: bool = True
    signup_timestamp: Optional[int] = None
    last_update_timestamp: Optional[int] = None

class RawUserData(BaseModel):  # voor data direct uit database
    name: str
    email_address: str
    user_id: int
    saldo: float
    update_kasgeld: bool = True
    signup_timestamp: Optional[int] = None
    last_update_timestamp: Optional[int] = None
    admin: bool = False
    banned: bool = False


class TransactionField(BaseModel):
    amount: float
    title: str
    description: str
    transaction_timestamp: int | None = None


class RawTransactionData(BaseModel):
    transaction_id: int
    title: str
    description: str
    amount: float
    transaction_timestamp: int
    record_creation_timestamp: int
    user_id: Optional[int] = None
