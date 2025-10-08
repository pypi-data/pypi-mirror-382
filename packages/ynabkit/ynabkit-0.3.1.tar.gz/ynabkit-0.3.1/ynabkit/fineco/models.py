import dataclasses
import datetime


@dataclasses.dataclass
class CreditCardTransaction:
    owner: str
    card_number: str
    transaction_date: datetime.datetime
    registration_date: datetime.datetime
    description: str
    operation_state: str
    operation_type: str
    circuit: str
    transaction_type: str
    amount: float
    payee: str

    @property
    def timestamp(self) -> datetime.datetime:
        return self.transaction_date

@dataclasses.dataclass
class AccountTransaction:
    date: datetime.datetime
    amount: float
    description: str
    description_full: str
    state: str
    moneymap_category: str
    payee: str

    @property
    def timestamp(self) -> datetime.datetime:
        return self.date
    