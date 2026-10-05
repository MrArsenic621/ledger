from datetime import datetime, timezone
from decimal import Decimal
import pytest
from src.domain import Currency, AccountType, Asset, AssetType, AssetStatus

@pytest.fixture
def usd():
    return Currency(code="USD", name="US Dollar", symbol="$")

def test_create_asset(usd):
    acquisition_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    asset = Asset(
        id="asset-1",
        name="MacBook Pro",
        account_id="acc-100", # Refers to the Asset Account in the ledger
        original_cost=Decimal("2000.00"),
        acquisition_date=acquisition_date,
        type=AssetType.PHYSICAL,
        status=AssetStatus.ACTIVE,
        currency=usd
    )
    
    assert asset.name == "MacBook Pro"
    assert asset.original_cost == Decimal("2000.00")
    assert asset.type == AssetType.PHYSICAL
    assert asset.status == AssetStatus.ACTIVE
    assert asset.acquisition_date == acquisition_date
    assert asset.currency.code == "USD"
