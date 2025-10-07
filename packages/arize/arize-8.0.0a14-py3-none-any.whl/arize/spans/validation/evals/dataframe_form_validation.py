import logging
import re
from typing import List

import pandas as pd

from arize.logging import log_a_list
from arize.spans.columns import (
    EVAL_COLUMN_PATTERN,
    EVAL_EXPLANATION_PATTERN,
    EVAL_LABEL_PATTERN,
    EVAL_SCORE_PATTERN,
    SPAN_SPAN_ID_COL,
)
from arize.spans.conversion import isMissingValue
from arize.spans.validation.common.errors import (
    InvalidDataFrameColumnContentTypes,
)

logger = logging.getLogger(__name__)


def log_info_dataframe_extra_column_names(
    df: pd.DataFrame | None,
) -> None:
    if df is None:
        return None
    irrelevant_columns = [
        col
        for col in df.columns
        if not (
            pd.Series(col).str.match(EVAL_COLUMN_PATTERN).any()
            or col == SPAN_SPAN_ID_COL.name
        )
    ]
    if irrelevant_columns:
        logger.info(
            "The following columns do not follow the evaluation column naming convention "
            f"and will be ignored: {log_a_list(values=irrelevant_columns, join_word='and')}. "
            "Evaluation columns must be named as follows: "
            "- eval.<your-eval-name>.label"
            "- eval.<your-eval-name>.score"
            "- eval.<your-eval-name>.explanation"
        )
    return None


def check_dataframe_column_content_type(
    df: pd.DataFrame,
) -> List[InvalidDataFrameColumnContentTypes]:
    wrong_labels_cols = []
    wrong_scores_cols = []
    wrong_explanations_cols = []
    errors = []
    eval_label_re = re.compile(EVAL_LABEL_PATTERN)
    eval_score_re = re.compile(EVAL_SCORE_PATTERN)
    eval_explanation_re = re.compile(EVAL_EXPLANATION_PATTERN)
    for column in df.columns:
        if column == SPAN_SPAN_ID_COL.name and not all(
            isinstance(value, str) for value in df[column]
        ):
            errors.append(
                InvalidDataFrameColumnContentTypes(
                    invalid_type_cols=[SPAN_SPAN_ID_COL.name],
                    expected_type="string",
                ),
            )
        if eval_label_re.match(column):
            if not all(
                isinstance(value, str) or isMissingValue(value)
                for value in df[column]
            ):
                wrong_labels_cols.append(column)
        elif eval_score_re.match(column):
            if not all(
                isinstance(value, (int, float)) or isMissingValue(value)
                for value in df[column]
            ):
                wrong_scores_cols.append(column)
        elif eval_explanation_re.match(column) and not all(
            isinstance(value, str) or isMissingValue(value)
            for value in df[column]
        ):
            wrong_explanations_cols.append(column)

    if wrong_labels_cols:
        errors.append(
            InvalidDataFrameColumnContentTypes(
                invalid_type_cols=wrong_labels_cols,
                expected_type="strings",
            ),
        )
    if wrong_scores_cols:
        errors.append(
            InvalidDataFrameColumnContentTypes(
                invalid_type_cols=wrong_scores_cols,
                expected_type="ints or floats",
            ),
        )
    if wrong_explanations_cols:
        errors.append(
            InvalidDataFrameColumnContentTypes(
                invalid_type_cols=wrong_explanations_cols,
                expected_type="strings",
            ),
        )
    return errors
