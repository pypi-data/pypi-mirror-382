"""Type stubs for xsxl - High-Performance Excel to Arrow Parser"""

from typing import Iterator, List, Optional, Any
import pyarrow as pa
import pandas as pd
import polars as pl

__version__: str

class Workbook:
    """
    Excel workbook - loads metadata only.

    Opening a workbook only loads metadata (sheet names, structure), not the
    actual worksheet data.
    """

    def __init__(self, path: str) -> None:
        """
        Open an Excel workbook (metadata only).

        Args:
            path: Path to the Excel file

        Raises:
            ValueError: If file format is invalid
            IOError: If file cannot be read
        """
        ...

    def __getitem__(self, name: str) -> Worksheet:
        """
        Get worksheet by name.

        Args:
            name: Sheet name

        Returns:
            Worksheet reference (no data loaded)

        Raises:
            KeyError: If sheet not found
        """
        ...

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over sheet names.

        Yields:
            Sheet name
        """
        ...

    @property
    def sheets(self) -> List[str]:
        """List of sheet names."""
        ...


class Worksheet:
    """
    Reference to a worksheet - no data loaded.
    """

    @property
    def name(self) -> str:
        """Sheet name."""
        ...

    def get_range(
        self,
        reference: str,
        batch_size: int = 1000,
        transpose: bool = False,
        has_headers: bool = True
    ) -> Range:
        """
        Create a range reference (no data loaded yet).

        Args:
            reference: Excel reference (e.g., "A1:Z100", "A:Z", "5:10")
            batch_size: Number of rows per batch (default: 1000, min: 1, max: 100,000)
                Note: Ignored in transpose mode - entire range returned in single batch
            transpose: Transpose mode for column-based data (default: False)
                When True, Excel columns become Arrow rows (entire range in one batch)
            has_headers: First row contains headers (default: True)

        Returns:
            Range reference

        Raises:
            ValueError: If reference is invalid or batch_size out of bounds
        """
        ...


class Range:
    """
    Lazy range reference - parsing happens on iteration/conversion.
    """

    def iter_batches(self) -> Iterator[pa.RecordBatch]:
        """
        Iterate over Arrow RecordBatches.

        This is the core streaming method that yields data in batches.
        Each batch is a PyArrow RecordBatch with typed columns.

        Note: In transpose mode, the entire range is returned in a single batch
        regardless of batch_size setting, because Excel columns become Arrow rows.

        The GIL is released during parsing for true parallelism.

        Yields:
            PyArrow RecordBatch with typed columns

        Raises:
            ValueError: If range is invalid or data cannot be parsed
            IOError: If file cannot be read
        """
        ...

    def to_arrow(self, limit: Optional[int] = None) -> pa.Table:
        """
        Convert range to PyArrow Table.

        Streams all batches and combines them into a single table.

        Args:
            limit: Optional limit on number of batches to read

        Returns:
            PyArrow Table with typed columns

        Raises:
            ValueError: If range is invalid or data cannot be parsed
            IOError: If file cannot be read
        """
        ...

    def to_pandas(self, **kwargs: Any) -> pd.DataFrame:
        """
        Convert range to Pandas DataFrame.

        Args:
            **kwargs: Additional arguments passed to pyarrow.Table.to_pandas()

        Returns:
            Pandas DataFrame

        Raises:
            ValueError: If range is invalid or data cannot be parsed
            IOError: If file cannot be read
        """
        ...

    def to_polars(self, **kwargs: Any) -> pl.DataFrame:
        """
        Convert range to Polars DataFrame.

        Args:
            **kwargs: Additional arguments passed to polars.from_arrow()

        Returns:
            Polars DataFrame

        Raises:
            ValueError: If range is invalid or data cannot be parsed
            IOError: If file cannot be read
            ImportError: If polars is not installed
        """
        ...


def open(path: str) -> Workbook:
    """
    Open an Excel workbook (metadata only, no data loaded).

    Args:
        path: Path to the Excel file

    Returns:
        Workbook object with lazy loading

    Raises:
        ValueError: If file format is invalid
        IOError: If file cannot be read

    Example:
        >>> import xsxl
        >>> wb = xsxl.open("data.xlsx")
        >>> sheet = wb["Sheet1"]
        >>> df = sheet.get_range("A1:Z100").to_pandas()
    """
    ...


__all__ = ["open", "Workbook", "Worksheet", "Range"]
