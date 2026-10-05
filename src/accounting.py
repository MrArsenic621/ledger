from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class PostingType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class Posting(BaseModel):
    account_id: str
    amount: Decimal
    type: PostingType


class JournalEntry(BaseModel):
    id: str
    timestamp: datetime
    postings: list[Posting]
    description: str = ""

    def is_balanced(self) -> bool:
        total_debits = sum(
            p.amount for p in self.postings if p.type == PostingType.DEBIT
        )
        total_credits = sum(
            p.amount for p in self.postings if p.type == PostingType.CREDIT
        )
        return total_debits == total_credits
