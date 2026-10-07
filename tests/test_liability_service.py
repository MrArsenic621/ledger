from datetime import datetime, timezone
from decimal import Decimal
import pytest
from src.domain import Account, AccountType, Currency
from src.liability_strategies import LiabilityStatus, LiabilityType, LoanConfig
from src.services import LiabilityService


@pytest.fixture
def usd():
    return Currency(code="USD", name="US Dollar", symbol="$")


@pytest.fixture
def bank(usd):
    return Account(
        id="acc-bank",
        name="Bank",
        balance=Decimal("1000.00"),
        currency=usd,
        type=AccountType.ASSET,
    )


@pytest.fixture
def interest_expense(usd):
    return Account(
        id="acc-int",
        name="Interest Expense",
        balance=Decimal("0.00"),
        currency=usd,
        type=AccountType.EXPENSE,
    )


def test_originate_liability(bank, usd):
    config = LoanConfig(
        interest_rate=Decimal("0.10"),
        installment_amount=Decimal("100.00"),
        installments=12,
    )
    liability, liability_account = LiabilityService.originate(
        name="Personal Loan",
        type=LiabilityType.LOAN,
        currency=usd,
        balance=Decimal("1000.00"),
        original_principal=Decimal("1000.00"),
        config=config,
        funding_account=bank,
    )

    assert liability.name == "Personal Loan"
    assert liability.balance == Decimal("1000.00")
    # Origination debits bank (increases asset)
    assert bank.balance == Decimal("2000.00")
    # Origination credits liability account (increases liability)
    assert liability_account.balance == Decimal("1000.00")


def test_process_payment(bank, interest_expense, usd):
    config = LoanConfig(
        interest_rate=Decimal("0.0"),
        installment_amount=Decimal("120.00"),
        installments=10,
    )  # Using 0 interest for simple math
    liability, liability_account = LiabilityService.originate(
        name="Car Loan",
        type=LiabilityType.LOAN,
        currency=usd,
        balance=Decimal("1000.00"),
        original_principal=Decimal("1000.00"),
        config=config,
        funding_account=bank,
    )

    # After origination, bank is 2000
    LiabilityService.process_payment(
        liability, bank, interest_expense, liability_account
    )

    # 1000 / 10 = 100 principal, 20 interest
    assert liability.balance == Decimal("900.00")  # 1000 - 100
    assert bank.balance == Decimal("1880.00")  # 2000 - 120
    assert interest_expense.balance == Decimal("20.00")  # 0 + 20
    assert liability_account.balance == Decimal("900.00")  # 1000 - 100

    # Test final payment status
    liability.balance = Decimal("100.00")
    liability_account.balance = Decimal("100.00")

    LiabilityService.process_payment(
        liability, bank, interest_expense, liability_account
    )
    assert liability.status == LiabilityStatus.PAID
    assert liability.balance == Decimal("0.00")
