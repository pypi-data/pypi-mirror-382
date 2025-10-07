from __future__ import annotations

from typing import TYPE_CHECKING, List

from arize.exceptions.base import InvalidDataFrameIndex
from arize.spans.validation.common.errors import (
    InvalidDataFrameDuplicateColumns,
    InvalidDataFrameMissingColumns,
)

if TYPE_CHECKING:
    import pandas as pd


def check_dataframe_index(
    dataframe: pd.DataFrame,
) -> List[InvalidDataFrameIndex]:
    if (dataframe.index != dataframe.reset_index(drop=True).index).any():
        return [InvalidDataFrameIndex()]
    return []


def check_dataframe_required_column_set(
    df: pd.DataFrame,
    required_columns: List[str],
) -> List[InvalidDataFrameMissingColumns]:
    existing_columns = set(df.columns)
    missing_cols = []
    for col in required_columns:
        if col not in existing_columns:
            missing_cols.append(col)

    if missing_cols:
        return [InvalidDataFrameMissingColumns(missing_cols=missing_cols)]
    return []


def check_dataframe_for_duplicate_columns(
    df: pd.DataFrame,
) -> List[InvalidDataFrameDuplicateColumns]:
    # Get the duplicated column names from the dataframe
    duplicate_columns = df.columns[df.columns.duplicated()]
    if not duplicate_columns.empty:
        return [InvalidDataFrameDuplicateColumns(duplicate_columns)]
    return []
