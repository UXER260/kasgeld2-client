# client/models.py
# bevat alle pydantic models
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class AdminLoginField(BaseModel):
    email: str
    password: str


class AdminSignupField(BaseModel):
    name: str
    email: str
    password: str


class UserSignupData(BaseModel):
    name: str
    saldo: float
    signup_timestamp: Optional[int] = None
    last_update_timestamp: Optional[int] = None


class RawUserData(BaseModel):  # voor data direct uit database
    user_id: int
    name: str
    saldo: float
    last_update_timestamp: int
    signup_timestamp: int


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
    record_creation_timestamp: int
    transaction_timestamp: int
    user_id: int
