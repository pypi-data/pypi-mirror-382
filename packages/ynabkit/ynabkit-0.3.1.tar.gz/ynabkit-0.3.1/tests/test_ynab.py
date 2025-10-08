from click.testing import CliRunner
from unittest.mock import Mock, patch
import datetime
from ynabkit.cli import cli, describe
from ynabkit.fineco.models import AccountTransaction
from ynabkit import payee


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("cli, version ")


def test_describe_date_filtering():
    """Test that the describe function properly filters transactions by start and end dates."""
    
    # Create mock transactions with different dates
    transactions = [
        AccountTransaction(
            date=datetime.datetime(2023, 1, 15),
            amount=100.0,
            description="Transaction 1",
            description_full="Transaction 1 Full",
            state="completed",
            moneymap_category="category1",
            payee="Payee 1"
        ),
        AccountTransaction(
            date=datetime.datetime(2023, 2, 15),
            amount=200.0,
            description="Transaction 2", 
            description_full="Transaction 2 Full",
            state="completed",
            moneymap_category="category2",
            payee="Payee 2"
        ),
        AccountTransaction(
            date=datetime.datetime(2023, 3, 15),
            amount=300.0,
            description="Transaction 3",
            description_full="Transaction 3 Full", 
            state="completed",
            moneymap_category="category3",
            payee="Payee 3"
        ),
    ]
    
    # Create mock input and output objects
    mock_input = Mock()
    mock_input.read.return_value = transactions
    
    mock_output = Mock()
    mock_output.table.return_value = "mocked table output"
    
    # Create mock payee resolver
    mock_payee_resolver = Mock(spec=payee.PayeeResolver)
    mock_payee_resolver.unresolved = []
    
    # Test 1: No date filtering - should return all transactions
    with patch('ynabkit.cli.click.echo') as mock_echo:
        describe(mock_input, mock_output, mock_payee_resolver, "table", None, None)
        mock_output.table.assert_called_once()
        filtered_transactions = mock_output.table.call_args[0][0]
        assert len(filtered_transactions) == 3
    
    # Reset mocks
    mock_output.reset_mock()
    
    # Test 2: Start date filtering - should return transactions from Feb 1st onwards
    start_date = datetime.datetime(2023, 2, 1)
    with patch('ynabkit.cli.click.echo') as mock_echo:
        describe(mock_input, mock_output, mock_payee_resolver, "table", start_date, None)
        filtered_transactions = mock_output.table.call_args[0][0]
        assert len(filtered_transactions) == 2
        assert all(t.timestamp >= start_date for t in filtered_transactions)
    
    # Reset mocks  
    mock_output.reset_mock()
    
    # Test 3: End date filtering - should return transactions up to Feb 28th
    end_date = datetime.datetime(2023, 2, 28)
    with patch('ynabkit.cli.click.echo') as mock_echo:
        describe(mock_input, mock_output, mock_payee_resolver, "table", None, end_date)
        filtered_transactions = mock_output.table.call_args[0][0]
        assert len(filtered_transactions) == 2
        assert all(t.timestamp <= end_date for t in filtered_transactions)
    
    # Reset mocks
    mock_output.reset_mock()
    
    # Test 4: Both start and end date filtering - should return only Feb transaction
    start_date = datetime.datetime(2023, 2, 1)
    end_date = datetime.datetime(2023, 2, 28)
    with patch('ynabkit.cli.click.echo') as mock_echo:
        describe(mock_input, mock_output, mock_payee_resolver, "table", start_date, end_date)
        filtered_transactions = mock_output.table.call_args[0][0]
        assert len(filtered_transactions) == 1
        assert filtered_transactions[0].timestamp >= start_date
        assert filtered_transactions[0].timestamp <= end_date
        assert filtered_transactions[0].description == "Transaction 2"
    
    # Reset mocks
    mock_output.reset_mock()
    
    # Test 5: Date range with no matching transactions
    start_date = datetime.datetime(2023, 4, 1)
    end_date = datetime.datetime(2023, 4, 30)
    with patch('ynabkit.cli.click.echo') as mock_echo:
        describe(mock_input, mock_output, mock_payee_resolver, "table", start_date, end_date)
        filtered_transactions = mock_output.table.call_args[0][0]
        assert len(filtered_transactions) == 0
