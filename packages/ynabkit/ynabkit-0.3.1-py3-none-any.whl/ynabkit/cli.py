import sys
import yaml
import datetime
import click

from .fineco.inputs import AccountTransactionsInput, CreditCardTransactionsInput
from .fineco.outputs import CreditCardTransactionsOutput, AccountTransactionsOutput
from .satispay.inputs import TransactionsInput
from .satispay.outputs import TransactionsOutput
from .n26.inputs import TransactionsInput as N26TransactionsInput
from .n26.outputs import TransactionsOutput as N26TransactionsOutput
from . import payee


@click.group()
@click.version_option()
@click.option(
    "-p",
    "--payees-file",
    help="YAML file containing payee mappings",
    type=click.Path(exists=True),
    default="payees.yml",
)
@click.option(
    "-s",
    "--start-date",
    help="Start date",
    type=click.DateTime(),
    default=None,
)
@click.option(
    "-e",
    "--end-date",
    help="End date",
    type=click.DateTime(),
    default=None,
)
@click.pass_context
def cli(ctx: click.Context, payees_file: str, start_date: datetime.datetime = None, end_date: datetime.datetime = None):
    "CLI tool to support data import and export from YNAB"
    try:
        with open(payees_file, "r") as f:
            mappings = yaml.safe_load(f)
            
            payee_resolver = payee.PayeeResolver()
            payee_resolver.load_mappings(mappings)

            ctx.ensure_object(dict)
            ctx.obj["payee_resolver"] = payee_resolver
            ctx.obj["start_date"] = start_date
            ctx.obj["end_date"] = end_date

    except Exception as e:
        raise click.BadParameter(
            f"Error loading payee mappings from {payees_file}: {e}",
            param=ctx.params.get("payees_file"),
            param_hint="payees-file",
        ) from e

@cli.group()
def fineco():
    "Fineco related commands"


@cli.group()
def satispay():
    "Satispay related commands"


@cli.group()
def n26():
    "N26 related commands"


@fineco.command(name="describe-account-transactions")
@click.argument(
    "excel-file-name",
)
@click.option(
    "-o",
    "--output-format",
    help="Output format",
    type=click.Choice(["table", "csv", "json"]),
    default="table",
)
@click.pass_context
def describe_account_transactions(ctx: click.Context, excel_file_name: str, output_format: str):
    "Read an .xlsx file containing bank account transactions and output the in a table, CSV or JSON file"
    payee_resolver = ctx.obj["payee_resolver"]
    describe(
        AccountTransactionsInput(excel_file_name, payee_resolver),
        AccountTransactionsOutput(),
        payee_resolver,
        output_format,
        ctx.obj.get("start_date"),
        ctx.obj.get("end_date"),
    )


@fineco.command(name="describe-card-transactions")
@click.argument(
    "excel-file-name",
)
@click.option(
    "-o",
    "--output-format",
    help="Output format",
    type=click.Choice(["table", "csv", "json"]),
    default="table",
)
@click.option(
    "-c",
    "--circuit",
    help="Credit card circuit",
    type=click.Choice(["ALL", "BANCOMAT", "VISA", "MASTERCARD"]),
    default="ALL",
)
@click.pass_context
def describe_card_transactions(ctx: click.Context, excel_file_name: str, output_format: str, circuit: str = None):
    "Read an .xlsx file containing credit card transactions and output the in a table or a CSV file"
    payee_resolver = ctx.obj["payee_resolver"]
    describe(
        CreditCardTransactionsInput(excel_file_name, payee_resolver, circuit=circuit),
        CreditCardTransactionsOutput(),
        payee_resolver,
        output_format,
        ctx.obj.get("start_date"),
        ctx.obj.get("end_date"),
    )

@satispay.command(name="describe-transactions")
@click.argument(
    "excel-file-name",
)
@click.option(
    "-o",
    "--output-format",
    help="Output format",
    type=click.Choice(["table", "csv", "json"]),
    default="table",
)
@click.option(
    "-e",
    "--exclude-kinds",
    help="Exclude kinds",
    type=click.Choice([
        "BANK",
        "C2B",
        "P2P",
    ]),
    default=None,
)
@click.pass_context
def describe_transactions(ctx: click.Context, excel_file_name: str, output_format: str, exclude_kinds: str = None):
    "Read an .xlsx file containing credit card transactions and output the in a table or a CSV file"
    payee_resolver = ctx.obj["payee_resolver"]
    describe(
        TransactionsInput(
            excel_file_name,
            exclude_kinds=exclude_kinds,
            payee_resolver=payee_resolver
        ),
        TransactionsOutput(),
        payee_resolver,
        output_format,
        ctx.obj.get("start_date"),
        ctx.obj.get("end_date"),
    )

@n26.command(name="describe-transactions")
@click.argument(
    "csv-file-name",
)
@click.option(
    "-s",
    "--skip-header",
    help="Skip the header row",
    default=True,
)
@click.option(
    "-o",
    "--output-format",
    help="Output format",
    type=click.Choice(["table", "csv", "json"]),
    default="table",
)
@click.pass_context
def describe_n26_transactions(ctx: click.Context, csv_file_name: str, skip_header: bool, output_format: str):
    "Read an .csv file containing N26 transactions and output the in a table or a CSV file"
    payee_resolver = ctx.obj["payee_resolver"]
    describe(
        N26TransactionsInput(
            csv_file_name,
            skip_header=skip_header,
            payee_resolver=payee_resolver
        ),
        N26TransactionsOutput(),
        payee_resolver,
        output_format,
        ctx.obj.get("start_date"),
        ctx.obj.get("end_date"),
    )


def describe(input, output, payee_resolver: payee.PayeeResolver, output_format: str, start_date: datetime.datetime = None, end_date: datetime.datetime = None):
    """Read from input and write to output in the specified format."""
    transactions = input.read()
    
    if start_date:
        transactions = [t for t in transactions if t.timestamp >= start_date]
    if end_date:
        transactions = [t for t in transactions if t.timestamp <= end_date]

    if output_format == "table":
        click.echo(output.table(transactions))
    elif output_format == "csv":
        click.echo(output.csv(transactions))
    elif output_format == "json":
        click.echo(output.json(transactions))
    
    if payee_resolver.unresolved:
        click.echo(f"There are {len(payee_resolver.unresolved)} unresolved memos:", file=sys.stderr)
        for memo in payee_resolver.unresolved:
            click.echo(f"  - {memo}", file=sys.stderr)
