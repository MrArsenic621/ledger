from datetime import datetime, timezone
from decimal import Decimal
import pytest
from src.domain import Currency
from src.accounting import Liability, LiabilityType

@pytest.fixture
def usd():
    return Currency(code="USD", name="US Dollar", symbol="$")

def test_create_liability(usd):
    due_date = datetime(2026, 12, 31, tzinfo=timezone.utc)
    liability = Liability(
        id="liab-1",
        name="Car Loan",
        type=LiabilityType.LOAN,
        currency=usd,
        principal=Decimal("20000.00"),
        interest_rate=Decimal("0.05"),
        balance=Decimal("20000.00"),
        next_payment_date=due_date
    )
    
    assert liability.name == "Car Loan"
    assert liability.principal == Decimal("20000.00")
    assert liability.balance == Decimal("20000.00")
    assert liability.type == LiabilityType.LOAN
    assert liability.next_payment_date == due_date
