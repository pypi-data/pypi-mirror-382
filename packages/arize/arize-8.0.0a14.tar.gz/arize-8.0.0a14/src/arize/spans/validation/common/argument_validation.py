from typing import Any, List

import pandas as pd

from arize.exceptions.base import InvalidFieldTypeConversion
from arize.spans.validation.common.errors import InvalidTypeArgument


def check_field_convertible_to_str(
    project_name: Any,
    model_version: Any = None,
) -> List[InvalidFieldTypeConversion]:
    wrong_fields = []
    if project_name is not None and not isinstance(project_name, str):
        try:
            str(project_name)
        except Exception:
            wrong_fields.append("project_name")
    if model_version is not None and not isinstance(model_version, str):
        try:
            str(model_version)
        except Exception:
            wrong_fields.append("model_version")

    if wrong_fields:
        return [InvalidFieldTypeConversion(wrong_fields, "string")]
    return []


def check_dataframe_type(
    dataframe,
) -> List[InvalidTypeArgument]:
    if not isinstance(dataframe, pd.DataFrame):
        return [
            InvalidTypeArgument(
                wrong_arg=dataframe,
                arg_name="dataframe",
                arg_type="pandas DataFrame",
            )
        ]
    return []


def check_datetime_format_type(
    dt_fmt: Any,
) -> List[InvalidTypeArgument]:
    if not isinstance(dt_fmt, str):
        return [
            InvalidTypeArgument(
                wrong_arg=dt_fmt,
                arg_name="dateTime format",
                arg_type="string",
            )
        ]
    return []
