from datetime import UTC, datetime
from decimal import Decimal

from src.accounting import JournalEntry, Posting, PostingType
from src.domain import (
    Account,
    AccountType,
    Asset,
    AssetStatus,
    AssetType,
    Currency,
    Transaction,
    TransactionType,
)
from src.liability_strategies import (
    BNPLConfig,
    BorrowingConfig,
    Liability,
    LiabilityStatus,
    LiabilityStrategyFactory,
    LiabilityType,
    LoanConfig,
)


class TransactionService:
    def __init__(self):
        pass

    @staticmethod
    def process_transaction(transaction: Transaction) -> Account:
        """
        Process a single transaction and return the result.
        """
        if transaction.amount <= 0:
            raise ValueError("Transaction amount must be positive.")

        if transaction.currency.code != transaction.account.currency.code:
            raise ValueError("Transaction currency must match account currency.")

        if transaction.type == TransactionType.EXPENSE:
            if transaction.amount > transaction.account.balance:
                raise ValueError("Insufficient funds for the expense transaction.")
            transaction.account.balance -= transaction.amount
        elif transaction.type == TransactionType.INCOME:
            transaction.account.balance += transaction.amount

        return transaction.account

    @staticmethod
    def process_transfer(
        source_account: Account,
        destination_account: Account,
        amount: float,
        currency: Currency,
        timestamp: datetime,
    ) -> tuple[Account, Account]:
        """
        Process a transfer between two accounts.
        """
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")

        if (
            source_account.currency.code != currency.code
            or destination_account.currency.code != currency.code
        ):
            raise ValueError("Transfer currency must match both account currencies.")

        if amount > source_account.balance:
            raise ValueError("Insufficient funds for the transfer.")

        source_account.balance -= amount
        destination_account.balance += amount

        return (source_account, destination_account)


class TransactionRepository:
    def __init__(self):
        self.transactions = []

    def save(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)

    def list_all(self) -> list[Transaction]:
        return self.transactions

    def get_summary(self) -> dict[str, float]:
        return {
            "total_income": sum(
                t.amount for t in self.transactions if t.type == "income"
            ),
            "total_expense": sum(
                t.amount for t in self.transactions if t.type == "expense"
            ),
            "net_balance": sum(
                t.amount if t.type == "income" else -t.amount for t in self.transactions
            ),
        }


class AccountingService:
    def __init__(self):
        pass

    @staticmethod
    def apply_entry(entry: JournalEntry, accounts: dict[str, Account]):
        if not entry.is_balanced():
            raise ValueError("Journal entry is not balanced.")

        for posting in entry.postings:
            account = accounts.get(posting.account_id)
            if not account:
                raise ValueError(f"Account {posting.account_id} not found.")

            if account.type in [AccountType.ASSET, AccountType.EXPENSE]:
                if posting.type == PostingType.DEBIT:
                    account.balance += posting.amount
                elif posting.type == PostingType.CREDIT:
                    account.balance -= posting.amount
            elif account.type in [
                AccountType.LIABILITY,
                AccountType.EQUITY,
                AccountType.REVENUE,
                AccountType.INCOME,
            ]:
                if posting.type == PostingType.DEBIT:
                    account.balance -= posting.amount
                elif posting.type == PostingType.CREDIT:
                    account.balance += posting.amount

    @staticmethod
    def verify_ledger_integrity(accounts: list[Account]) -> bool:
        debit = 0
        credit = 0

        for account in accounts:
            if account.type in [AccountType.ASSET, AccountType.EXPENSE]:
                debit += account.balance
            elif account.type in [
                AccountType.LIABILITY,
                AccountType.EQUITY,
                AccountType.REVENUE,
                AccountType.INCOME,
            ]:
                credit += account.balance

        is_balanced = debit == credit
        if not is_balanced:
            raise ValueError(
                f"Ledger integrity check failed: Total Debit ({debit}) != Total Credit ({credit})"
            )

        return is_balanced


class LifecycleService:
    def __init__(self):
        pass

    @staticmethod
    def acquire(
        name: str,
        cost: Decimal,
        account: Account,
        type: AssetType,
        timestamp: datetime,
    ) -> tuple[Asset, Account]:
        if cost <= 0:
            raise ValueError("Acquisition cost must be positive.")

        if account.balance < cost:
            raise ValueError("Insufficient funds in the account for acquisition.")

        asset_account = Account(
            id=f"asset-account-{datetime.now(UTC).timestamp()}",
            name=f"{name} Account",
            balance=Decimal("0.00"),
            currency=account.currency,
            type=AccountType.ASSET,
        )

        asset = Asset(
            id=f"asset-{datetime.now(UTC).timestamp()}",
            name=name,
            original_cost=cost,
            account_id=asset_account.id,
            acquisition_date=timestamp,
            type=type,
            status=AssetStatus.ACTIVE,
            currency=asset_account.currency,
        )

        debit_posting = Posting(
            account_id=asset_account.id,
            amount=cost,
            type=PostingType.DEBIT,
        )
        credit_posting = Posting(
            account_id=account.id,
            amount=cost,
            type=PostingType.CREDIT,
        )
        journal_entry = JournalEntry(
            id=f"je-{datetime.now(UTC).timestamp()}",
            timestamp=timestamp,
            postings=[debit_posting, credit_posting],
            description=f"Acquisition of asset {name}",
        )

        try:
            AccountingService.apply_entry(
                journal_entry, {account.id: account, asset_account.id: asset_account}
            )
        except ValueError as e:
            raise ValueError(f"Failed to apply journal entry: {e}")

        return asset, asset_account

    @staticmethod
    def dispose(
        asset: Asset,
        disposal_amount: Decimal,
        funding_account: Account,
        asset_account: Account,
        expense_account: Account,
    ) -> None:
        if asset.status != AssetStatus.ACTIVE:
            raise ValueError("Only active assets can be disposed.")

        credit_posting = Posting(
            account_id=asset_account.id,
            amount=asset.original_cost,
            type=PostingType.CREDIT,
        )
        debit_posting = Posting(
            account_id=funding_account.id,
            amount=disposal_amount,
            type=PostingType.DEBIT,
        )
        expense_or_loss_posting = Posting(
            account_id=expense_account.id,
            amount=asset.original_cost - disposal_amount,
            type=PostingType.DEBIT,
        )
        journal_entry = JournalEntry(
            id=f"je-{datetime.now(UTC).timestamp()}",
            timestamp=datetime.now(UTC),
            postings=[debit_posting, credit_posting, expense_or_loss_posting],
            description=f"Disposal of asset {asset.name}",
        )

        AccountingService.apply_entry(
            journal_entry,
            {
                funding_account.id: funding_account,
                asset_account.id: asset_account,
                expense_account.id: expense_account,
            },
        )

        asset.status = AssetStatus.SOLD


class LiabilityService:
    def __init__(self):
        pass

    @staticmethod
    def originate(
        name: str,
        type: LiabilityType,
        currency: Currency,
        balance: Decimal,
        original_principal: Decimal,
        config: LoanConfig | BNPLConfig | BorrowingConfig,
        funding_account: Account,
    ) -> tuple[Liability, Account]:
        liability_account = Account(
            id=f"liability-account-{datetime.now(UTC).timestamp()}",
            name=name,
            balance=Decimal("0.00"),
            currency=currency,
            type=AccountType.LIABILITY,
        )
        liability = Liability(
            id=f"liability-{datetime.now(UTC).timestamp()}",
            name=name,
            type=type,
            currency=currency,
            balance=balance,
            account_id=liability_account.id,
            original_principal=original_principal,
            config=config,
        )

        debit_posting = Posting(
            account_id=funding_account.id,
            amount=original_principal,
            type=PostingType.DEBIT,
        )
        credit_posting = Posting(
            account_id=liability_account.id,
            amount=original_principal,
            type=PostingType.CREDIT,
        )
        journal_entry = JournalEntry(
            id=f"je-{datetime.now(UTC).timestamp()}",
            timestamp=datetime.now(UTC),
            postings=[debit_posting, credit_posting],
            description=f"Creating liability {liability.name}",
        )
        AccountingService.apply_entry(
            journal_entry,
            {
                liability_account.id: liability_account,
                funding_account.id: funding_account,
            },
        )

        return liability, liability_account

    @staticmethod
    def process_payment(
        liability: Liability,
        funding_account: Account,
        expense_account: Account,
        liability_account: Account,
    ):
        liability_strategy = LiabilityStrategyFactory.get_strategy(liability.type)
        if liability_strategy.is_fully_paid(liability):
            raise ValueError("Liability is already fully paid.")

        next_payment = liability_strategy.calculate_next_payment(liability)

        liability.balance -= next_payment["principal"]

        principal_debit_posting = Posting(
            account_id=liability_account.id,
            amount=next_payment["principal"],
            type=PostingType.DEBIT,
        )
        interest_debit_posting = Posting(
            account_id=expense_account.id,
            amount=next_payment["interest"],
            type=PostingType.DEBIT,
        )
        credit_posting = Posting(
            account_id=funding_account.id,
            amount=next_payment["total_amount"],
            type=PostingType.CREDIT,
        )
        journal_entry = JournalEntry(
            id=f"je-{datetime.now(UTC).timestamp()}",
            timestamp=datetime.now(UTC),
            postings=[principal_debit_posting, interest_debit_posting, credit_posting],
            description=f"Payment for liability {liability.name}",
        )

        try:
            AccountingService.apply_entry(
                journal_entry,
                {
                    liability.account_id: liability_account,
                    funding_account.id: funding_account,
                    expense_account.id: expense_account,
                },
            )
        except Exception as e:
            print(f"Error occurred while applying journal entry: {e}")
            liability.balance += next_payment["principal"]

        if liability_strategy.is_fully_paid(liability):
            liability.status = LiabilityStatus.PAID
