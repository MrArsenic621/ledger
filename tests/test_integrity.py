from decimal import Decimal
import pytest
from src.domain import Account, AccountType, Currency
from src.services import AccountingService

@pytest.fixture
def usd():
    return Currency(code="USD", name="US Dollar", symbol="$")

def test_verify_ledger_integrity_balanced(usd):
    # Assets: 1000, Expenses: 100
    # Liabilities: 500, Equity: 400, Revenue: 200
    # 1000 + 100 = 1100
    # 500 + 400 + 200 = 1100
    
    accounts = [
        Account(id="a1", name="Bank", balance=Decimal("1000.00"), currency=usd, type=AccountType.ASSET),
        Account(id="a2", name="Food", balance=Decimal("100.00"), currency=usd, type=AccountType.EXPENSE),
        Account(id="l1", name="Loan", balance=Decimal("500.00"), currency=usd, type=AccountType.LIABILITY),
        Account(id="e1", name="Capital", balance=Decimal("400.00"), currency=usd, type=AccountType.EQUITY),
        Account(id="r1", name="Sales", balance=Decimal("200.00"), currency=usd, type=AccountType.REVENUE),
    ]
    
    # Should not raise exception
    AccountingService.verify_ledger_integrity(accounts)

def test_verify_ledger_integrity_unbalanced(usd):
    # Assets: 1000, Expenses: 100 (Total 1100)
    # Liabilities: 500, Equity: 400 (Total 900)
    # Unbalanced!
    
    accounts = [
        Account(id="a1", name="Bank", balance=Decimal("1000.00"), currency=usd, type=AccountType.ASSET),
        Account(id="a2", name="Food", balance=Decimal("100.00"), currency=usd, type=AccountType.EXPENSE),
        Account(id="l1", name="Loan", balance=Decimal("500.00"), currency=usd, type=AccountType.LIABILITY),
        Account(id="e1", name="Capital", balance=Decimal("400.00"), currency=usd, type=AccountType.EQUITY),
    ]
    
    with pytest.raises(ValueError, match="Ledger integrity check failed"):
        AccountingService.verify_ledger_integrity(accounts)
