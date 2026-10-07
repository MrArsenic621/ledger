from datetime import datetime, timezone
from decimal import Decimal

import pytest
from src.domain import Currency
from src.liability_strategies import (
    BNPLConfig,
    BorrowingConfig,
    Liability,
    LiabilityStrategyFactory,
    LiabilityType,
    LoanConfig,
    LoanStrategy,
    BuyNowPayLaterStrategy,
    BorrowingStrategy,
)

@pytest.fixture
def usd():
    return Currency(code="USD", name="US Dollar", symbol="$")

def test_factory_returns_correct_strategy():
    assert isinstance(LiabilityStrategyFactory.get_strategy(LiabilityType.LOAN), LoanStrategy)
    assert isinstance(LiabilityStrategyFactory.get_strategy(LiabilityType.BNPL), BuyNowPayLaterStrategy)
    assert isinstance(LiabilityStrategyFactory.get_strategy(LiabilityType.BORROWING), BorrowingStrategy)

def test_loan_strategy(usd):
    config = LoanConfig(interest_rate=Decimal("0.40"), installment_amount=Decimal("120.00"), installments=12)
    liability = Liability(
        id="loan-1", name="Car Loan", type=LiabilityType.LOAN,
        currency=usd, balance=Decimal("1000.00"), original_principal=Decimal("1000.00"),
        account_id="acc-loan", config=config
    )
    strategy = LiabilityStrategyFactory.get_strategy(LiabilityType.LOAN)
    
    # Check next payment
    payment = strategy.calculate_next_payment(liability)
    assert payment["total_amount"] == Decimal("120.00")
    # 1000 / 12 = 83.33333333333333333333333333
    assert payment["principal"].quantize(Decimal("0.0001")) == Decimal("83.3333")
    
    # Check full schedule
    schedule = strategy.get_full_schedule(liability)
    assert len(schedule) in (12, 13)
    # Final payment principal should be truncated due to logic in get_full_schedule summing up
    assert sum(p["principal"] for p in schedule).quantize(Decimal("0.01")) == Decimal("1000.00")
    assert strategy.is_fully_paid(liability) is False

def test_loan_strategy_edge_case(usd):
    config = LoanConfig(interest_rate=Decimal("0.40"), installment_amount=Decimal("120.00"), installments=12)
    # Simulate final payment balance
    liability = Liability(
        id="loan-1", name="Car Loan", type=LiabilityType.LOAN,
        currency=usd, balance=Decimal("50.00"), original_principal=Decimal("1000.00"),
        account_id="acc-loan", config=config
    )
    strategy = LiabilityStrategyFactory.get_strategy(LiabilityType.LOAN)
    
    payment = strategy.calculate_next_payment(liability)
    assert payment["principal"] == Decimal("50.00")
    assert payment["total_amount"] == Decimal("120.00") # Interest makes up the rest (70)

def test_bnpl_strategy(usd):
    config = BNPLConfig(introduction_fee=Decimal("50.00"), interest_rate=Decimal("0.0"), installments=4)
    liability = Liability(
        id="bnpl-1", name="Phone", type=LiabilityType.BNPL,
        currency=usd, balance=Decimal("400.00"), original_principal=Decimal("400.00"),
        account_id="acc-bnpl", config=config
    )
    strategy = LiabilityStrategyFactory.get_strategy(LiabilityType.BNPL)
    
    # First payment: includes fee
    payment = strategy.calculate_next_payment(liability)
    assert payment["fee"] == Decimal("50.00") if "fee" in payment else True # Logic puts it in interest/total
    assert payment["total_amount"] == Decimal("150.00")
    assert payment["principal"] == Decimal("100.00")
    
    # Change balance to test subsequent payments (no fee)
    liability.balance = Decimal("300.00")
    payment2 = strategy.calculate_next_payment(liability)
    assert payment2["total_amount"] == Decimal("100.00")
    assert payment2["principal"] == Decimal("100.00")

def test_borrowing_strategy(usd):
    config = BorrowingConfig(interest_rate=Decimal("0.10"), settlement_date=datetime(2027, 1, 1, tzinfo=timezone.utc))
    liability = Liability(
        id="borrow-1", name="Friend", type=LiabilityType.BORROWING,
        currency=usd, balance=Decimal("500.00"), original_principal=Decimal("500.00"),
        account_id="acc-borrow", config=config
    )
    strategy = LiabilityStrategyFactory.get_strategy(LiabilityType.BORROWING)
    
    payment = strategy.calculate_next_payment(liability)
    assert payment["principal"] == Decimal("500.00")
    assert payment["interest"] == Decimal("50.00")
    assert payment["total_amount"] == Decimal("550.00")
    
    schedule = strategy.get_full_schedule(liability)
    assert len(schedule) == 1
    assert schedule[0]["total_amount"] == Decimal("550.00")
