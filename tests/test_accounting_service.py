from decimal import Decimal
from datetime import datetime, timezone
import pytest
from src.accounting import JournalEntry, Posting, PostingType
from src.services import AccountService
from src.domain import Account, Currency, AccountType

@pytest.fixture
def usd():
    return Currency(code="USD", name="US Dollar", symbol="$")

def test_apply_balanced_entry(usd):
    # Setup accounts
    # Bank (Asset) - Credit decreases it
    acc_bank = Account(id="acc-1", name="Bank", balance=Decimal("1000.00"), currency=usd, type=AccountType.ASSET)
    # Expense (Expense) - Debit increases it
    acc_expense = Account(id="acc-2", name="Keyboard", balance=Decimal("0.00"), currency=usd, type=AccountType.EXPENSE)
    
    # Create entry: Debit expense $100, Credit bank $100
    entry = JournalEntry(
        id="je-1",
        timestamp=datetime.now(timezone.utc),
        postings=[
            Posting(account_id="acc-2", amount=Decimal("100.00"), type=PostingType.DEBIT),
            Posting(account_id="acc-1", amount=Decimal("100.00"), type=PostingType.CREDIT),
        ]
    )
    
    # User to implement: AccountingService.apply_entry(entry, [acc_bank, acc_expense])
    # Mapping account IDs for the service to find
    accounts = {acc.id: acc for acc in [acc_bank, acc_expense]}
    AccountService.apply_entry(entry, accounts)
    
    assert acc_bank.balance == Decimal("900.00")  # Asset Credit decreases
    assert acc_expense.balance == Decimal("100.00") # Expense Debit increases
