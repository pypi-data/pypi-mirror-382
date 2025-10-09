# pytest-dataguard

A pytest plugin for validating CSV data files as part of your test suite. It helps ensure your data files meet quality standards by checking for null values and enforcing uniqueness constraints on specified columns.

## Features
- **Null value checks**: Ensure your CSV files have no missing values.
- **Uniqueness checks**: Verify that specified columns contain only unique values.
- **Easy integration**: Run data validation as part of your regular pytest workflow.

## Installation

Install via pip:

```bash
pip install pytest-dataguard
```

Or install from source:

```bash
pip install .
```

## Usage

Run pytest with the plugin and specify the options:

```bash
pytest --file path/to/data.csv [--not_null] [--unique column1 --unique column2]
```

- `--file`: Path to the CSV file to validate (required).
- `--not_null`: Check that there are no null values in the file (optional, enabled by default).
- `--unique`: Specify one or more columns to check for uniqueness. Can be used multiple times.

### Example

Suppose you have a CSV file `data.csv` and want to ensure there are no nulls and that the `id` column is unique:

```bash
pytest --file data.csv --unique id
```

To check multiple columns for uniqueness:

```bash
pytest --file data.csv --unique id --unique email
```

## How it works

When you run pytest with the `pytest-dataguard` options, the plugin will:
- Load the specified CSV file using [Polars](https://pola.rs/)
- Check for null values `--not_null` is set by default
- Check that specified columns have unique values if `--unique` is used
- Fail the test session if any validation fails

## Requirements
- Python 3.8+
- [pytest](https://pytest.org/)
- [polars](https://pola.rs/)

## Contributing
Contributions are welcome! Please open issues or submit pull requests.

## License
[MIT License](LICENSE)
