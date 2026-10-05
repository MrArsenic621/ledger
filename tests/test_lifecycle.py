from datetime import datetime, timezone
from decimal import Decimal
import pytest
from src.domain import Account, AccountType, Currency, AssetStatus, AssetType
from src.services import LifecycleService

@pytest.fixture
def usd():
    return Currency(code="USD", name="US Dollar", symbol="$")

@pytest.fixture
def bank(usd):
    return Account(id="acc-1", name="Bank", balance=Decimal("1000.00"), currency=usd, type=AccountType.ASSET)

def test_acquire_asset(bank, usd):
    asset, asset_account = LifecycleService.acquire(
        name="Laptop",
        cost=Decimal("500.00"),
        account=bank,
        type=AssetType.PHYSICAL,
        timestamp=datetime.now(timezone.utc)
    )
    
    assert asset.name == "Laptop"
    assert asset.status == AssetStatus.ACTIVE
    assert bank.balance == Decimal("500.00") # 1000 - 500
    assert asset_account.balance == Decimal("500.00")

def test_dispose_asset(bank, usd):
    # Setup: Acquire first
    asset, asset_account = LifecycleService.acquire(
        name="Phone",
        cost=Decimal("1000.00"),
        account=bank,
        type=AssetType.PHYSICAL,
        timestamp=datetime.now(timezone.utc)
    )
    # bank balance is now 0 (1000 - 1000)
    
    # Create Expense account for loss
    loss_account = Account(id="acc-loss", name="Loss", balance=Decimal("0.00"), currency=usd, type=AccountType.EXPENSE)
    
    # Dispose: Sell for 200
    LifecycleService.dispose(asset, Decimal("200.00"), bank, asset_account, loss_account)
    
    assert asset.status == AssetStatus.SOLD
    # 0 (start) + 200 (disposal) = 200 bank balance
    assert bank.balance == Decimal("200.00")
    # Loss account should be 800
    assert loss_account.balance == Decimal("800.00")
