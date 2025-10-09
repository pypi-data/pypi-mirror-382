import pytest
import polars as pl
from pytest_dataguard.plugin import DataGuardPlugin


class DummyConfig:
    def __init__(self, file=None, not_null=True, unique=None):
        self._file = file
        self._not_null = not_null
        self._unique = unique or []

    def getoption(self, name):
        if name == "--file":
            return self._file
        if name == "--not_null":
            return self._not_null
        if name == "--unique":
            return self._unique
        return None


def test_read_file_success(tmp_path):
    # Create a sample CSV file
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("a,b\n1,2\n3,4\n")
    config = DummyConfig(file=str(csv_path), not_null=True, unique=[])
    plugin = DataGuardPlugin(config)
    df = plugin.read_file()
    assert df.shape == (2, 2)
    assert set(df.columns) == {"a", "b"}


def test_read_file_not_found(tmp_path):
    config = DummyConfig(file=str(tmp_path / "nofile.csv"))
    plugin = DataGuardPlugin(config)
    with pytest.raises(FileNotFoundError):
        plugin.read_file()


def test_get_columns_not_null():
    df = pl.DataFrame({"a": [1, None, 3], "b": [4, 5, 6], "c": [None, None, None]})
    config = DummyConfig(file="dummy.csv", not_null=True, unique=[])
    plugin = DataGuardPlugin(config)
    result = plugin.get_columns_not_null(df)
    assert set(result) == {"a", "c"}


def test_get_columns_unique():
    df = pl.DataFrame({"x": [1, 2, 2, 4], "y": [1, 2, 3, 4]})
    config = DummyConfig(file="dummy.csv", not_null=True, unique=["x", "y"])
    plugin = DataGuardPlugin(config)
    result = plugin.get_columns_unique(df)
    assert result == ["x"]


def test_get_columns_unique_column_not_exist():
    df = pl.DataFrame({"a": [1, 2, 3]})
    config = DummyConfig(file="dummy.csv", not_null=True, unique=["b"])
    plugin = DataGuardPlugin(config)
    with pytest.raises(ValueError):
        plugin.get_columns_unique(df)
