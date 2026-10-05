from datetime import datetime, timezone
import pytest
from src.domain import Account, Category, Currency, Transaction, TransactionType
from src.services import TransactionService, TransactionRepository

@pytest.fixture
def repo():
    return TransactionRepository()

@pytest.fixture
def usd():
    return Currency(code="USD", name="US Dollar", symbol="$")

def test_save_and_list_transactions(repo, usd):
    account = Account(id="acc-1", name="Bank", balance=1000.0, currency=usd)
    tx = Transaction(
        id="tx-1", amount=100.0, currency=usd, 
        category=Category(id="cat-1", name="Food", type="expense"),
        type=TransactionType.EXPENSE, account=account,
        timestamp=datetime.now(timezone.utc)
    )
    repo.save(tx)
    assert len(repo.list_all()) == 1
    assert repo.list_all()[0].id == "tx-1"

def test_summary_calculation(repo, usd):
    account = Account(id="acc-1", name="Bank", balance=1000.0, currency=usd)
    
    # 2 incomes, 1 expense
    repo.save(Transaction(id="t1", amount=500.0, currency=usd, category=Category(id="c1", name="S", type="income"), type=TransactionType.INCOME, account=account, timestamp=datetime.now(timezone.utc)))
    repo.save(Transaction(id="t2", amount=500.0, currency=usd, category=Category(id="c1", name="S", type="income"), type=TransactionType.INCOME, account=account, timestamp=datetime.now(timezone.utc)))
    repo.save(Transaction(id="t3", amount=200.0, currency=usd, category=Category(id="c2", name="F", type="expense"), type=TransactionType.EXPENSE, account=account, timestamp=datetime.now(timezone.utc)))
    
    summary = repo.get_summary()
    assert summary["total_income"] == 1000.0
    assert summary["total_expense"] == 200.0
    assert summary["net_balance"] == 800.0
