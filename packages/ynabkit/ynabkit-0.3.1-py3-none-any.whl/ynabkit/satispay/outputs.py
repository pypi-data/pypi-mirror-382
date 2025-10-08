import csv
import io
import json
from typing import List

from rich.console import Console
from rich.table import Table

from .models import Transaction


class TransactionsOutput:
    """Output a list of Transaction objects in a table or a CSV file"""

    def table(self, transactions: List[Transaction]) -> str:
        """Renders the transactions as a table."""
        console = Console(file=io.StringIO())
        
        console.print(f"Found {len(transactions)} transactions")

        # Create a new table
        table = Table(
            title="Transactions",
            # box=box.SIMPLE,
        )

        # Add columns
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("State")
        table.add_column("Kind")
        table.add_column("Date")
        table.add_column("Amount")
        table.add_column("Currency")
        table.add_column("Extra info")

        # Add rows
        for transaction in transactions:
            table.add_row(
                transaction.id,
                transaction.name,
                transaction.state,
                transaction.kind,
                str(transaction.date),
                str(transaction.amount),
                transaction.currency,
                transaction.extra_info,
            )

        # turn table into a string using the Console
        console.print(table)

        return console.file.getvalue()

    def csv(self, transactions: List[Transaction]) -> str:
        """Renders the transactions as a CSV string.
        
        It produces CSV using the YNAB format. See https://docs.youneedabudget.com/article/921-formatting-csv-file
        to learn more about the format.
        """
        output = io.StringIO()
        
        writer = csv.writer(output)
        writer.writerow(["Date", "Payee", "Memo", "Amount"])
        for transaction in transactions:
            memo = f"{transaction.name}: {transaction.extra_info or ''}"
            writer.writerow([
                transaction.date.strftime("%m/%d/%Y"),
                transaction.payee,
                memo,
                str(transaction.amount),
            ])

        return output.getvalue()

    def json(self, transactions: List[Transaction]) -> str:
        """Renders the transactions as a JSON string."""
        return json.dumps(transactions, cls=TransactionEncoder, indent=4)


class TransactionEncoder(json.JSONEncoder):
    def default(self, obj: Transaction):
        return {
            "id": obj.id,
            "name": obj.name,
            "state": obj.state,
            "kind": obj.kind,
            "date": obj.date.isoformat(),
            "amount": obj.amount,
            "currency": obj.currency,
            "extra_info": obj.extra_info,
            "payee": obj.payee,
        }
