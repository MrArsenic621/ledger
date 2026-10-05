from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class Currency(BaseModel):
    code: str
    name: str
    symbol: str


class Category(BaseModel):
    id: str
    name: str
    type: str


class Account(BaseModel):
    id: str
    name: str
    balance: float
    currency: Currency


class Transaction(BaseModel):
    id: str
    amount: float
    currency: Currency
    category: Category
    type: TransactionType
    account: Account
    timestamp: datetime
    description: str = None
