from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING, List

from arize.spans.columns import SPAN_SPAN_ID_COL
from arize.spans.validation.common import (
    argument_validation as common_arg_validation,
)
from arize.spans.validation.common import (
    dataframe_form_validation as common_df_validation,
)
from arize.spans.validation.common import (
    value_validation as common_value_validation,
)
from arize.spans.validation.evals import (
    dataframe_form_validation as df_validation,
)
from arize.spans.validation.evals import (
    value_validation,
)

if TYPE_CHECKING:
    import pandas as pd

    from arize.exceptions.base import ValidationError


def validate_argument_types(
    evals_dataframe: pd.DataFrame,
    project_name: str,
    model_version: str | None = None,
) -> List[ValidationError]:
    checks = chain(
        common_arg_validation.check_field_convertible_to_str(
            project_name, model_version
        ),
        common_arg_validation.check_dataframe_type(evals_dataframe),
    )
    return list(checks)


def validate_dataframe_form(
    evals_dataframe: pd.DataFrame,
) -> List[ValidationError]:
    df_validation.log_info_dataframe_extra_column_names(evals_dataframe)
    checks = chain(
        # Common
        common_df_validation.check_dataframe_index(evals_dataframe),
        common_df_validation.check_dataframe_required_column_set(
            evals_dataframe, required_columns=[SPAN_SPAN_ID_COL.name]
        ),
        common_df_validation.check_dataframe_for_duplicate_columns(
            evals_dataframe
        ),
        # Eval specific
        df_validation.check_dataframe_column_content_type(evals_dataframe),
    )
    return list(checks)


def validate_values(
    evals_dataframe: pd.DataFrame,
    project_name: str,
    model_version: str | None = None,
) -> List[ValidationError]:
    checks = chain(
        # Common
        common_value_validation.check_invalid_project_name(project_name),
        common_value_validation.check_invalid_model_version(model_version),
        # Eval specific
        value_validation.check_eval_cols(evals_dataframe),
        value_validation.check_eval_columns_null_values(evals_dataframe),
    )
    return list(checks)
