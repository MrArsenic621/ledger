from decimal import Decimal
from datetime import datetime, timezone
import pytest

from src.accounting import JournalEntry, Posting, PostingType

def test_balanced_journal_entry():
    entry = JournalEntry(
        id="je-1",
        timestamp=datetime.now(timezone.utc),
        postings=[
            Posting(account_id="acc-1", amount=Decimal("100.00"), type=PostingType.DEBIT),
            Posting(account_id="acc-2", amount=Decimal("100.00"), type=PostingType.CREDIT),
        ]
    )
    assert entry.is_balanced() is True

def test_unbalanced_journal_entry():
    entry = JournalEntry(
        id="je-2",
        timestamp=datetime.now(timezone.utc),
        postings=[
            Posting(account_id="acc-1", amount=Decimal("100.00"), type=PostingType.DEBIT),
            Posting(account_id="acc-2", amount=Decimal("50.00"), type=PostingType.CREDIT),
        ]
    )
    assert entry.is_balanced() is False
