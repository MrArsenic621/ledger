from datetime import datetime, timezone
from decimal import Decimal
import pytest
from src.domain import Account, AccountType, Category, Currency, Transaction, TransactionType
from src.services import TransactionRepository

@pytest.fixture
def repo():
    return TransactionRepository()

@pytest.fixture
def usd():
    return Currency(code="USD", name="US Dollar", symbol="$")

def test_save_and_list_transactions(repo, usd):
    account = Account(id="acc-1", name="Bank", balance=Decimal("1000.00"), currency=usd, type=AccountType.ASSET)
    tx = Transaction(
        id="tx-1", amount=Decimal("100.00"), currency=usd, 
        category=Category(id="cat-1", name="Food", type="expense"),
        type=TransactionType.EXPENSE, account=account,
        timestamp=datetime.now(timezone.utc)
    )
    repo.save(tx)
    assert len(repo.list_all()) == 1
    assert repo.list_all()[0].id == "tx-1"

def test_summary_calculation(repo, usd):
    account = Account(id="acc-1", name="Bank", balance=Decimal("1000.00"), currency=usd, type=AccountType.ASSET)
    
    # 2 incomes, 1 expense
    repo.save(Transaction(id="t1", amount=Decimal("500.00"), currency=usd, category=Category(id="c1", name="S", type="income"), type=TransactionType.INCOME, account=account, timestamp=datetime.now(timezone.utc)))
    repo.save(Transaction(id="t2", amount=Decimal("500.00"), currency=usd, category=Category(id="c1", name="S", type="income"), type=TransactionType.INCOME, account=account, timestamp=datetime.now(timezone.utc)))
    repo.save(Transaction(id="t3", amount=Decimal("200.00"), currency=usd, category=Category(id="c2", name="F", type="expense"), type=TransactionType.EXPENSE, account=account, timestamp=datetime.now(timezone.utc)))
    
    summary = repo.get_summary()
    assert summary["total_income"] == Decimal("1000.00")
    assert summary["total_expense"] == Decimal("200.00")
    assert summary["net_balance"] == Decimal("800.00")
