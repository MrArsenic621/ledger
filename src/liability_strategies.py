from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel

from src.domain import Currency


class LiabilityType(str, Enum):
    LOAN = "loan"
    BNPL = "buy_now_pay_later"
    BORROWING = "borrowing"


class LoanConfig(BaseModel):
    interest_rate: Decimal
    installment_amount: Decimal
    installments: int


class BNPLConfig(BaseModel):
    introduction_fee: Decimal
    interest_rate: Decimal
    installments: int


class BorrowingConfig(BaseModel):
    interest_rate: Decimal
    settlement_date: datetime


class Liability(BaseModel):
    id: str
    name: str
    type: LiabilityType
    currency: Currency
    balance: Decimal
    account_id: str
    original_principal: Decimal
    config: LoanConfig | BNPLConfig | BorrowingConfig


class AmortizationStrategy(ABC):
    @abstractmethod
    def calculate_next_payment(self, liability: Liability) -> dict[str, Decimal]:
        pass

    @abstractmethod
    def get_full_schedule(self, liability: Liability) -> list[dict[str, Decimal]]:
        pass

    @abstractmethod
    def is_fully_paid(self, liability: Liability) -> bool:
        pass


class LoanStrategy(AmortizationStrategy):
    def calculate_next_payment(self, liability: Liability) -> dict[str, Decimal]:
        if liability.balance <= 0:
            return {"amount": Decimal(0)}
        principal = liability.original_principal / liability.config.installments
        principal = min(principal, liability.balance)
        interest = liability.config.installment_amount - principal
        return {
            "total_amount": principal + interest,
            "principal": principal,
            "interest": interest,
        }

    def get_full_schedule(self, liability: Liability) -> list[dict[str, Decimal]]:
        monthly_principal = liability.original_principal / liability.config.installments
        monthly_interest = liability.config.installment_amount - monthly_principal
        simulated_balance = liability.balance
        schedule = []
        while simulated_balance > Decimal("0.01"):
            if simulated_balance < monthly_principal:
                monthly_principal = simulated_balance
                monthly_interest = (
                    liability.config.installment_amount - monthly_principal
                )
            payment = {
                "total_amount": round(monthly_principal + monthly_interest, 2),
                "principal": round(monthly_principal, 2),
                "interest": round(monthly_interest, 2),
            }
            schedule.append(payment)
            simulated_balance -= payment["principal"]
            simulated_balance = round(simulated_balance, 4) # avoid infinite decimal tail
        return schedule

    def is_fully_paid(self, liability: Liability) -> bool:
        return liability.balance <= 0


class BuyNowPayLaterStrategy(AmortizationStrategy):
    def calculate_next_payment(self, liability: Liability) -> dict[str, Decimal]:
        if liability.balance <= 0:
            return {"amount": Decimal(0)}
        if liability.balance == liability.original_principal:
            fee = liability.config.introduction_fee
        else:
            fee = Decimal(0)
        total_amount = fee + (
            liability.original_principal / liability.config.installments
        )
        principal = liability.original_principal / liability.config.installments
        interest = total_amount - principal

        return {
            "total_amount": total_amount,
            "principal": principal,
            "interest": interest,
        }

    def get_full_schedule(self, liability: Liability) -> list[dict[str, Decimal]]:
        monthly_principal = liability.original_principal / liability.config.installments
        monthly_interest = (
            liability.config.introduction_fee / liability.config.installments
        )
        simulated_balance = liability.balance
        schedule = []
        while simulated_balance > Decimal("0.01"):
            if simulated_balance < monthly_principal:
                monthly_principal = simulated_balance
                monthly_interest = (
                    liability.config.introduction_fee / liability.config.installments
                )
            payment = {
                "total_amount": round(monthly_principal + monthly_interest, 2),
                "principal": round(monthly_principal, 2),
                "interest": round(monthly_interest, 2),
            }
            schedule.append(payment)
            simulated_balance -= payment["principal"]
            simulated_balance = round(simulated_balance, 4)
        return schedule

    def is_fully_paid(self, liability: Liability) -> bool:
        return liability.balance <= 0


class BorrowingStrategy(AmortizationStrategy):
    def calculate_next_payment(self, liability: Liability) -> dict[str, Decimal]:
        return {
            "total_amount": liability.balance * (1 + liability.config.interest_rate),
            "principal": liability.balance,
            "interest": liability.balance * liability.config.interest_rate,
        }

    def get_full_schedule(self, liability: Liability) -> list[dict[str, Decimal]]:
        return [self.calculate_next_payment(liability)]

    def is_fully_paid(self, liability: Liability) -> bool:
        return liability.balance <= 0


class LiabilityStrategyFactory:
    _STRATEGIES = {  # noqa: RUF012
        LiabilityType.LOAN: LoanStrategy(),
        LiabilityType.BNPL: BuyNowPayLaterStrategy(),
        LiabilityType.BORROWING: BorrowingStrategy(),
    }

    @classmethod
    def get_strategy(cls, liability_type: LiabilityType) -> AmortizationStrategy:
        strategy = cls._STRATEGIES.get(liability_type)
        if not strategy:
            raise ValueError(f"No strategy found for liability type: {liability_type}")
        return strategy
