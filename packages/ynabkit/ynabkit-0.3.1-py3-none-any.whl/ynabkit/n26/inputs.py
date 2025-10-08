from typing import List, Callable
import csv
import datetime

from .models import Transaction


class TransactionsInput:
    """Read a CSV file containing N26 transactions and output a list of Transaction objects"""

    def __init__(self, csv_file_name: str, skip_header: bool, payee_resolver: Callable[[str], str]):
        self.csv_file_name = csv_file_name
        self.skip_header = skip_header
        self.resolve_payee = payee_resolver

    def read(self) -> List[Transaction]:
        """Read a CSV file containing N26 transactions and output a list of Transaction objects"""
        with open(self.csv_file_name, newline='') as csvfile:
            transactions = []

            reader = csv.reader(csvfile)
            if self.skip_header:
                next(reader)  # Skip the header row

            for row in reader:
                transactions.append(Transaction(
                    booking_date=datetime.datetime.strptime(row[0], "%Y-%m-%d"),
                    value_date=datetime.datetime.strptime(row[1], "%Y-%m-%d"),
                    partner_name=row[2],
                    partner_iban=row[3],
                    type=row[4],
                    payment_reference=row[5],
                    account_name=row[6],
                    amount_eur=float(row[7]),
                    original_amount=float(row[8]),
                    original_currency=row[9],
                    exchange_rate=float(row[10]),
                    payee=self.resolve_payee(row[2]),
                ))

            return transactions