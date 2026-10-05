from datetime import datetime, timezone
import pytest

from src.domain import Account, Category, Currency, Transaction, TransactionType


def test_create_currency():
    usd = Currency(code="USD", name="US Dollar", symbol="$")
    assert usd.code == "USD"
    assert usd.name == "US Dollar"
    assert usd.symbol == "$"


def test_create_category():
    category = Category(id="cat-1", name="Utilities", type="expense")
    assert category.id == "cat-1"
    assert category.name == "Utilities"
    assert category.type == "expense"


def test_create_account():
    usd = Currency(code="USD", name="US Dollar", symbol="$")
    account = Account(id="acc-1", name="Bank Account", balance=1000.0, currency=usd)
    assert account.id == "acc-1"
    assert account.name == "Bank Account"
    assert account.balance == 1000.0
    assert account.currency.code == "USD"


def test_create_transaction_expense():
    usd = Currency(code="USD", name="US Dollar", symbol="$")
    account = Account(id="acc-1", name="Bank Account", balance=1000.0, currency=usd)
    category = Category(id="cat-1", name="Utilities", type="expense")

    tx = Transaction(
        id="tx-1",
        amount=50.0,
        currency=usd,
        category=category,
        type=TransactionType.EXPENSE,
        account=account,
        timestamp=datetime.now(timezone.utc),
    )
    assert tx.id == "tx-1"
    assert tx.amount == 50.0
    assert tx.type == TransactionType.EXPENSE
    assert tx.account.id == "acc-1"
    assert tx.currency.code == "USD"
    assert tx.category.id == "cat-1"
