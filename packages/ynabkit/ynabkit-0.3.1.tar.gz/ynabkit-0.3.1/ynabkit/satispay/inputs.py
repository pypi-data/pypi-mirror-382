from typing import List, Callable
import datetime

from openpyxl import load_workbook

from .models import Transaction


class TransactionsInput:

    def __init__(self, excel_file: str, payee_resolver: Callable[[str], str], exclude_kinds: List[str] = None):
        self.excel_file = excel_file
        self.exclude_kinds = exclude_kinds
        self.payee_resolver = payee_resolver

    def read(self) -> List[Transaction]:
        """Read a credit card statement and output a list of Transaction objects"""
        # Open the workbook
        workbook = load_workbook(filename=self.excel_file)
        ws = workbook.active

        transactions = []
        for row in ws.iter_rows(min_row=2, max_col=8):
            # Skip if the kind is in the exclude list
            if self.exclude_kinds and row[3].value in self.exclude_kinds:
                continue

            t = Transaction(
                id=row[0].value,
                name=row[1].value,
                state=row[2].value,
                kind=row[3].value,
                # Parses dates in the format "18 Sep 2023 at 4:15:01 PM" format.
                date=self._parse_date(row[4].value),
                amount=self._parse_amount(row[5].value),
                currency=row[6].value,
                extra_info=row[7].value.rstrip() if row[7].value else None,
                payee=self.payee_resolver(row[1].value),
            )

            transactions.append(t)

        return transactions

    def _parse_date(self, date_str: str) -> datetime.date:
        # try one of the following date formats
        date_formats = [
            '%d %b %Y at %I:%M:%S %p',
            '%d %b %Y at %H:%M:%S',
        ]
        for date_format in date_formats:
            try:
                return datetime.datetime.strptime(date_str, date_format)
            except ValueError:
                pass

        raise ValueError(f"Could not parse date {date_str}")

    def _parse_amount(self, amount_str: str) -> float:
        """
        Parse string amounts like "+40" or "-12,4" to float
        
        Args:
            amount_str: String representation of amount (e.g., "+40", "-12,4")
            
        Returns:
            float: The parsed amount
            
        Examples:
            >>> parse_amount("+40")
            40.0
            >>> parse_amount("-12,4")
            -12.4
            >>> parse_amount("1.234,56")
            1234.56        
        """
        return float(amount_str.replace(".", "").replace(",", "."))
