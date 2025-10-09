import typing

from odp.util.cheapdantic import BaseModel


class ColumnStats(BaseModel):
    """ColumnStats contains statistics about a column in a table"""

    name: str
    """name of the column"""

    metadata: typing.Optional[dict]
    """metadata of the column, if any"""

    type: str
    """type of the column, e.g., 'string', 'int', 'float', etc."""

    null_count: int
    """number of null values in the column"""

    num_values: int
    """number of non-null values in the column"""

    min: typing.Union[int, float, str, None]
    """minimum value in the column, if applicable"""

    max: typing.Union[int, float, str, None]
    """maximum value in the column, if applicable"""


class TableStats(BaseModel):
    """
    TableStats contains statistics about a table, including metadata, number of rows, columns.
    """

    num_rows: int
    """number of rows in the table"""

    size: int
    """size of the table in bytes, including metadata and schema"""

    columns: typing.Optional[list[ColumnStats]]
