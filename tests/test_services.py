from datetime import datetime, timezone
import pytest

from src.domain import Account, Category, Currency, Transaction, TransactionType
from src.services import TransactionService


@pytest.fixture
def usd():
    return Currency(code="USD", name="US Dollar", symbol="$")


@pytest.fixture
def eur():
    return Currency(code="EUR", name="Euro", symbol="€")


@pytest.fixture
def bank_account(usd):
    return Account(id="acc-1", name="Main Checking", balance=1000.0, currency=usd)


@pytest.fixture
def savings_account(usd):
    return Account(id="acc-2", name="Savings", balance=500.0, currency=usd)


@pytest.fixture
def salary_category():
    return Category(id="cat-salary", name="Salary", type="income")


@pytest.fixture
def groceries_category():
    return Category(id="cat-food", name="Groceries", type="expense")


def test_process_income(bank_account, salary_category, usd):
    service = TransactionService()
    tx = Transaction(
        id="tx-inc-1",
        amount=500.0,
        currency=usd,
        category=salary_category,
        type=TransactionType.INCOME,
        account=bank_account,
        timestamp=datetime.now(timezone.utc),
    )

    updated_account = service.process_transaction(tx)
    assert updated_account.balance == 1500.0


def test_process_expense(bank_account, groceries_category, usd):
    service = TransactionService()
    tx = Transaction(
        id="tx-exp-1",
        amount=150.0,
        currency=usd,
        category=groceries_category,
        type=TransactionType.EXPENSE,
        account=bank_account,
        timestamp=datetime.now(timezone.utc),
    )

    updated_account = service.process_transaction(tx)
    assert updated_account.balance == 850.0


def test_process_transfer(bank_account, savings_account, usd):
    service = TransactionService()
    source, destination = service.process_transfer(
        source_account=bank_account,
        destination_account=savings_account,
        amount=200.0,
        currency=usd,
        timestamp=datetime.now(timezone.utc),
    )

    assert source.balance == 800.0
    assert destination.balance == 700.0


def test_reject_negative_or_zero_amount(bank_account, salary_category, usd):
    service = TransactionService()
    tx = Transaction(
        id="tx-inv-1",
        amount=-100.0,
        currency=usd,
        category=salary_category,
        type=TransactionType.INCOME,
        account=bank_account,
        timestamp=datetime.now(timezone.utc),
    )

    with pytest.raises(ValueError, match="Transaction amount must be positive."):
        service.process_transaction(tx)


def test_reject_currency_mismatch(bank_account, salary_category, eur):
    service = TransactionService()
    tx = Transaction(
        id="tx-cur-1",
        amount=100.0,
        currency=eur,
        category=salary_category,
        type=TransactionType.INCOME,
        account=bank_account,
        timestamp=datetime.now(timezone.utc),
    )

    with pytest.raises(ValueError, match="Transaction currency must match account currency."):
        service.process_transaction(tx)
