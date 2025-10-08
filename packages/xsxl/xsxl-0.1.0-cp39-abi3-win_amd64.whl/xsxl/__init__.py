"""
xsxl - High-Performance Excel to Arrow Parser

A blazingly fast Python library for streaming Excel (XLSX) data directly to
Apache Arrow format, built in Rust with PyO3.
"""

from typing import TYPE_CHECKING

# Import Rust bindings
from xsxl._core import Workbook, Worksheet, Range, PatternBuilder, Pattern, PatternMatch, R

# Convenience function
def open(path: str) -> Workbook:
    """
    Open an Excel workbook (metadata only, no data loaded).

    Args:
        path: Path to the Excel file

    Returns:
        Workbook object with lazy loading

    Example:
        >>> wb = xsxl.open("data.xlsx")
        >>> sheet = wb["Sheet1"]
        >>> df = sheet.get_range("A1:Z100").to_pandas()
    """
    return Workbook(path)

__version__ = "0.1.0"
__all__ = ["open", "Workbook", "Worksheet", "Range", "PatternBuilder", "Pattern", "PatternMatch", "R"]
