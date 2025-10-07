import logging
from datetime import datetime, timedelta
from typing import List

import numpy as np
import pandas as pd
import pyarrow as pa

from arize.constants.ml import (
    MAX_FUTURE_YEARS_FROM_CURRENT_TIME,
    MAX_PAST_YEARS_FROM_CURRENT_TIME,
)
from arize.exceptions.parameters import InvalidModelVersion, InvalidProjectName
from arize.spans.columns import (
    SPAN_END_TIME_COL,
    SPAN_START_TIME_COL,
)
from arize.spans.validation.common.errors import (
    InvalidFloatValueInColumn,
    InvalidJsonStringInColumn,
    InvalidMissingValueInColumn,
    InvalidStartAndEndTimeValuesInColumn,
    InvalidStringLengthInColumn,
    InvalidStringValueNotAllowedInColumn,
    InvalidTimestampValueInColumn,
)
from arize.types import is_json_str

logger = logging.getLogger(__name__)


def check_invalid_project_name(
    project_name: str | None,
) -> List[InvalidProjectName]:
    # assume it's been coerced to string beforehand
    if (not isinstance(project_name, str)) or len(project_name.strip()) == 0:
        return [InvalidProjectName()]
    return []


def check_invalid_model_version(
    model_version: str | None = None,
) -> List[InvalidModelVersion]:
    if model_version is None:
        return []
    if not isinstance(model_version, str) or len(model_version.strip()) == 0:
        return [InvalidModelVersion()]

    return []


def check_string_column_value_length(
    df: pd.DataFrame,
    col_name: str,
    min_len: int,
    max_len: int,
    is_required: bool,
    must_be_json: bool = False,
) -> List[InvalidMissingValueInColumn | InvalidStringLengthInColumn]:
    if col_name not in df.columns:
        return []

    errors = []
    if is_required and df[col_name].isnull().any():
        errors.append(
            InvalidMissingValueInColumn(
                col_name=col_name,
            )
        )

    if not (
        # Check that the non-None values of the desired colum have a
        # string length between min_len and max_len
        # Does not check the None values
        df[~df[col_name].isnull()][col_name]
        .astype(str)
        .str.len()
        .between(min_len, max_len)
        .all()
    ):
        errors.append(
            InvalidStringLengthInColumn(
                col_name=col_name,
                min_length=min_len,
                max_length=max_len,
            )
        )
    if (
        must_be_json
        and not df[~df[col_name].isnull()][col_name].apply(is_json_str).all()
    ):
        errors.append(InvalidJsonStringInColumn(col_name=col_name))

    return errors


def check_string_column_allowed_values(
    df: pd.DataFrame,
    col_name: str,
    allowed_values: List[str],
    is_required: bool,
) -> List[InvalidMissingValueInColumn | InvalidStringValueNotAllowedInColumn]:
    if col_name not in df.columns:
        return []

    errors = []
    if is_required and df[col_name].isnull().any():
        errors.append(
            InvalidMissingValueInColumn(
                col_name=col_name,
            )
        )

    # We compare in lowercase
    allowed_values_lowercase = [v.lower() for v in allowed_values]
    if not (
        # Check that the non-None values of the desired colum have a
        # string values amongst the ones allowed
        # Does not check the None values
        df[~df[col_name].isnull()][col_name]
        .astype(str)
        .str.lower()
        .isin(allowed_values_lowercase)
        .all()
    ):
        errors.append(
            InvalidStringValueNotAllowedInColumn(
                col_name=col_name,
                allowed_values=allowed_values,
            )
        )
    return errors


# Checks to make sure there are no inf values in the column
def check_float_column_valid_numbers(
    df: pd.DataFrame,
    col_name: str,
) -> List[InvalidFloatValueInColumn]:
    if col_name not in df.columns:
        return []
    # np.isinf will fail on None values, change Nones to np.nan and check on that
    column_numeric = pd.to_numeric(df[col_name], errors="coerce")
    invalid_mask = np.isinf(column_numeric)
    invalid_exists = invalid_mask.any()

    if invalid_exists:
        error = [InvalidFloatValueInColumn(col_name=col_name)]
        return error
    return []


def check_value_columns_start_end_time(
    df: pd.DataFrame,
) -> List[
    InvalidMissingValueInColumn
    | InvalidTimestampValueInColumn
    | InvalidStartAndEndTimeValuesInColumn
]:
    errors = []
    errors += check_value_timestamp(
        df=df,
        col_name=SPAN_START_TIME_COL.name,
        is_required=SPAN_START_TIME_COL.required,
    )
    errors += check_value_timestamp(
        df=df,
        col_name=SPAN_END_TIME_COL.name,
        is_required=SPAN_END_TIME_COL.required,
    )
    if (
        SPAN_START_TIME_COL.name in df.columns
        and SPAN_END_TIME_COL.name in df.columns
        and (df[SPAN_START_TIME_COL.name] > df[SPAN_END_TIME_COL.name]).any()
    ):
        errors.append(
            InvalidStartAndEndTimeValuesInColumn(
                greater_col_name=SPAN_END_TIME_COL.name,
                less_col_name=SPAN_START_TIME_COL.name,
            )
        )
    return errors


def check_value_timestamp(
    df: pd.DataFrame,
    col_name: str,
    is_required: bool,
) -> List[InvalidMissingValueInColumn | InvalidTimestampValueInColumn]:
    # This check expects that timestamps have previously been converted to nanoseconds
    if col_name not in df.columns:
        return []

    errors = []
    if is_required and df[col_name].isnull().any():
        errors.append(
            InvalidMissingValueInColumn(
                col_name=col_name,
            )
        )

    now_t = datetime.now()
    lbound, ubound = (
        (
            now_t - timedelta(days=MAX_PAST_YEARS_FROM_CURRENT_TIME * 365)
        ).timestamp()
        * 1e9,
        (
            now_t + timedelta(days=MAX_FUTURE_YEARS_FROM_CURRENT_TIME * 365)
        ).timestamp()
        * 1e9,
    )

    # faster than pyarrow compute
    stats = df[col_name].agg(["min", "max"])

    ta = pa.Table.from_pandas(stats.to_frame())
    min_, max_ = ta.column(0)

    # Check if min/max are None before comparing (handles NaN input)
    min_val = min_.as_py()
    max_val = max_.as_py()

    if max_val is not None and max_val > now_t.timestamp() * 1e9:
        logger.warning(
            f"Detected future timestamp in column '{col_name}'. "
            "Caution when sending spans with future timestamps. "
            "Arize only stores 2 years worth of data. For example, if you sent spans "
            "to Arize from 1.5 years ago, and now send spans with timestamps of a year in "
            "the future, the oldest 0.5 years will be dropped to maintain the 2 years worth of data "
            "requirement."
        )

    if (min_val is not None and min_val < lbound) or (
        max_val is not None and max_val > ubound
    ):
        return [InvalidTimestampValueInColumn(timestamp_col_name=col_name)]

    return []
