from datetime import datetime, timezone
from decimal import Decimal
import pytest
from src.domain import Currency
from src.liability_strategies import Liability, LiabilityType, LoanConfig

@pytest.fixture
def usd():
    return Currency(code="USD", name="US Dollar", symbol="$")

def test_create_liability(usd):
    config = LoanConfig(interest_rate=Decimal("0.05"), installment_amount=Decimal("400.00"), installments=60)
    liability = Liability(
        id="liab-1",
        name="Car Loan",
        type=LiabilityType.LOAN,
        currency=usd,
        original_principal=Decimal("20000.00"),
        account_id="acc-liab-1",
        balance=Decimal("20000.00"),
        config=config
    )
    
    assert liability.name == "Car Loan"
    assert liability.original_principal == Decimal("20000.00")
    assert liability.balance == Decimal("20000.00")
    assert liability.type == LiabilityType.LOAN
