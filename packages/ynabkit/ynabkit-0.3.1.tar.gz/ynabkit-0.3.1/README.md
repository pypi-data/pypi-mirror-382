# ynabkit

[![PyPI](https://img.shields.io/pypi/v/ynabkit.svg)](https://pypi.org/project/ynabkit/)
[![Changelog](https://img.shields.io/github/v/release/zmoog/ynabkit?include_prereleases&label=changelog)](https://github.com/zmoog/ynabkit/releases)
[![Tests](https://github.com/zmoog/ynabkit/workflows/Test/badge.svg)](https://github.com/zmoog/ynabkit/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/zmoog/ynabkit/blob/master/LICENSE)

YNAB Kit is a CLI tool to support data import and export from YNAB. It provides tools to convert data from Fineco, N26, and Satispay export files to YNAB CSV format.

## Installation

Install this tool using `pip`:

    pip install ynabkit

## Usage

### Fineco Bank

Convert Fineco bank export files to YNAB format:

```bash
# Basic conversion
ynabkit fineco describe-transactions input.xlsx

# With payee configuration
ynabkit fineco describe-transactions input.xlsx --payees payees.yml
```

### N26 Bank

Convert N26 bank export files to YNAB format:

```bash
# Basic conversion
ynabkit n26 describe-transactions input.csv

# With payee configuration
ynabkit n26 describe-transactions input.csv --payees payees.yml
```

### Satispay

Convert Satispay export files to YNAB format:

```bash
# Basic conversion
ynabkit satispay describe-transactions input.csv

# Exclude specific transaction types
ynabkit satispay describe-transactions input.csv --exclude-kinds "Ricarica,Prelievo"

# With payee configuration
ynabkit satispay describe-transactions input.csv --payees payees.yml
```

### Payee Configuration

Create a `payees.yml` file to map transaction descriptions to specific payees:

```yaml
- name: Amazon
  patterns:
  - "AMAZON"
  - "AMAZON.*"
- name: Spotify
  patterns:
  - "SPOTIFY"
- name: Local Supermarket
  patterns:
  - ".*SUPERMARKET.*"
  - "CONAD"
  - "COOP"
```

For help with any command, run:

    ynabkit --help

You can also use:

    python -m ynabkit --help

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd ynabkit
    python -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
