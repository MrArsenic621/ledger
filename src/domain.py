from datetime import datetime
from decimal import Decimal
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


class AccountType(str, Enum):
    ASSET = "asset"
    EXPENSE = "expense"
    INCOME = "income"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"

class Account(BaseModel):
    id: str
    name: str
    balance: Decimal
    type: AccountType
    currency: Currency


class Transaction(BaseModel):
    id: str
    amount: Decimal
    currency: Currency
    category: Category
    type: TransactionType
    account: Account
    timestamp: datetime
    description: str = None

class AssetType(str, Enum):
    PHYSICAL = "physical"
    FINANCIAL = "financial"
    INVESTMENT = "investment"
    PROPERTY = "property"
    VEHICLE = "vehicle"

class AssetStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SOLD = "sold"
    DEPRECIATED = "depreciated"

class Asset(BaseModel):
    id: str
    name: str
    account_id: str
    original_cost: Decimal
    acquisition_date: datetime
    type: AssetType
    status: AssetStatus

