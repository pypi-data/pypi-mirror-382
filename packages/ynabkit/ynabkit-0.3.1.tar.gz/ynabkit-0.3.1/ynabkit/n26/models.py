import dataclasses
import datetime


@dataclasses.dataclass
class Transaction:
    booking_date: datetime.datetime
    value_date: datetime.datetime
    partner_name: str
    partner_iban: str
    type: str
    payment_reference: str
    account_name: str
    amount_eur: float
    original_amount: float
    original_currency: str
    exchange_rate: float
    payee: str

    @property
    def timestamp(self) -> datetime.datetime:
        return self.booking_date
