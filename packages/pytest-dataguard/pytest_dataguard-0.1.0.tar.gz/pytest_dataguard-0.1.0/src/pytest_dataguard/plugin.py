from __future__ import annotations

from typing import TYPE_CHECKING
from pathlib import Path
import polars as pl

if TYPE_CHECKING:
    from _pytest.config import Config, ExitCode
    from _pytest.main import Session
    from _pytest.terminal import TerminalReporter


class DataGuardPlugin:
    # Initialize the plugin with configuration options
    def __init__(self, config: Config):
        self.config = config
        self.file: Path = config.getoption("--file")
        self.not_null: bool = config.getoption("--not_null") or True
        self.unique: list[str] = config.getoption("--unique")
        self.reporter: TerminalReporter | None = None
        self._fail = False

    def read_file(self) -> pl.DataFrame:
        """Read the CSV file into a Polars DataFrame."""
        file_path = Path(self.file)
        if not file_path.exists():
            self._fail = True
            raise FileNotFoundError(f"The file {self.file} does not exist.")
        return pl.read_csv(self.file, separator=",")

    def get_columns_not_null(self, df: pl.DataFrame) -> list[str]:
        """Return a list of columns that contain null values."""
        melted = df.select(pl.all().is_null().sum()).melt(
            variable_name="column", value_name="null_count"
        )
        return melted.filter(pl.col("null_count") > 0).get_column("column").to_list()

    def get_columns_unique(self, df: pl.DataFrame) -> list[str]:
        """Return a list of columns that contain duplicate values."""
        bad = []

        # single-column uniqueness
        for col in self.unique:
            if col not in df.columns:
                self._fail = True
                raise ValueError(f"Column '{col}' does not exist.")
            num_dups = df.get_column(col).is_duplicated().sum()  # counts duplicates
            if num_dups > 0:
                bad.append(col)

        return bad

    def pytest_terminal_summary(self, terminalreporter: TerminalReporter) -> None:
        """Hook to add a summary to the terminal report."""
        self.reporter = terminalreporter
        if not self.file:
            self._fail = True
            terminalreporter.section("pytest-dataguard")
            terminalreporter.write_line(
                "No --file provided; skipping dataguard checks."
            )
            return
        try:
            df = self.read_file()
        except Exception as e:
            self._fail = True
            terminalreporter.write_line(f"Error reading file: {e}")
            return
        if self.not_null:
            try:
                columns_with_null = self.get_columns_not_null(df)
                if columns_with_null:
                    self._fail = True
                    terminalreporter.write_line(
                        f"Columns with null values: {', '.join(columns_with_null)}"
                    )
                else:
                    terminalreporter.write_line(
                        "All columns passed the not-null check."
                    )
            except Exception as e:
                self._fail = True
                terminalreporter.write_line(f"Error during not-null check: {e}")
        if self.unique:
            try:
                non_unique_columns = self.get_columns_unique(df)
                if non_unique_columns:
                    self._fail = True
                    terminalreporter.write_line(
                        f"Columns with duplicate values: {', '.join(non_unique_columns)}"
                    )
                else:
                    terminalreporter.write_line(
                        "All specified columns passed the unique check."
                    )
            except Exception as e:
                self._fail = True
                terminalreporter.write_line(f"Error during unique check: {e}")

    def pytest_sessionfinish(self, session: Session, exitstatus: ExitCode) -> None:
        """Hook to set the exit status based on validation results."""
        if self.reporter:
            self.reporter.write_line("Data validation completed.")
        if self._fail:
            session.exitstatus = 1
