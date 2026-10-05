from datetime import datetime

from src.domain import Account, Currency, Transaction, TransactionType


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
