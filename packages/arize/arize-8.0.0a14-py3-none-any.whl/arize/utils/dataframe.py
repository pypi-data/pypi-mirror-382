import re
from typing import List

import pandas as pd

from arize.types import BaseSchema


# Resets the dataframe index if it is not a RangeIndex
def reset_dataframe_index(dataframe: pd.DataFrame) -> None:
    if not isinstance(dataframe.index, pd.RangeIndex):
        drop = dataframe.index.name in dataframe.columns
        dataframe.reset_index(inplace=True, drop=drop)


def remove_extraneous_columns(
    df: pd.DataFrame,
    schema: BaseSchema | None = None,
    column_list: List[str] | None = None,
    regex: str | None = None,
) -> pd.DataFrame:
    relevant_columns = set()
    if schema is not None:
        relevant_columns.update(schema.get_used_columns())
    if column_list is not None:
        relevant_columns.update(column_list)
    if regex is not None:
        matched_regex_cols = []
        for col in df.columns:
            match_result = re.match(regex, col)
            if match_result:
                matched_regex_cols.append(col)
        relevant_columns.update(matched_regex_cols)

    final_columns = list(set(df.columns) & relevant_columns)
    return df.filter(items=final_columns)
