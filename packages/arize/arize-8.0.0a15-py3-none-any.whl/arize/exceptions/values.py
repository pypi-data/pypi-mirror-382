from collections.abc import Iterable
from typing import Dict, List, Optional

from arize.constants.ml import (
    MAX_FUTURE_YEARS_FROM_CURRENT_TIME,
    MAX_MULTI_CLASS_NAME_LENGTH,
    MAX_NUMBER_OF_MULTI_CLASS_CLASSES,
    MAX_PAST_YEARS_FROM_CURRENT_TIME,
    MAX_TAG_LENGTH,
)
from arize.exceptions.base import ValidationError
from arize.logging import log_a_list


class InvalidValueTimestamp(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Timestamp_Value"

    def __init__(self, timestamp_col_name: str) -> None:
        self.timestamp_col_name = timestamp_col_name

    def error_message(self) -> str:
        return (
            f"Prediction timestamp in {self.timestamp_col_name} is out of range. "
            f"Prediction timestamps must be within {MAX_FUTURE_YEARS_FROM_CURRENT_TIME} year "
            f"in the future and {MAX_PAST_YEARS_FROM_CURRENT_TIME} years in the past from "
            "the current time. If this is your pre-production data, you could also just "
            "remove the timestamp column from the Schema."
        )


class InvalidValueMissingValue(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Missing_Value"

    def __init__(
        self, name: str, wrong_values: str, column: Optional[str] = None
    ) -> None:
        self.name = name
        self.wrong_values = wrong_values
        self.column = column

    def error_message(self) -> str:
        if self.name in ["Prediction ID", "Prediction Group ID", "Rank"]:
            return f"{self.name} column '{self.column}' must not contain {self.wrong_values} values."
        else:
            return f"{self.name} must not contain {self.wrong_values} values."


class InvalidRankValue(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Rank_Value"

    def __init__(self, name: str, acceptable_range: str) -> None:
        self.name = name
        self.acceptable_range = acceptable_range

    def error_message(self) -> str:
        return (
            f"ranking column {self.name} is out of range. "
            f"Only values within {self.acceptable_range}  are accepted. "
        )


class InvalidStringLengthInColumn(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_String_Length_In_Column"

    def __init__(
        self, schema_name: str, col_name: str, min_length: int, max_length: int
    ) -> None:
        self.schema_name = schema_name
        self.col_name = col_name
        self.min_length = min_length
        self.max_length = max_length

    def error_message(self) -> str:
        return (
            f"{self.schema_name} column '{self.col_name}' contains invalid values. "
            f"Only string values of length between {self.min_length} and {self.max_length} are accepted."
        )


class InvalidTagLength(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Tag_Length"

    def __init__(self, cols: Iterable) -> None:
        self.wrong_value_columns = cols

    def error_message(self) -> str:
        return (
            f"Only tag values with less than or equal to {MAX_TAG_LENGTH} characters are supported. "
            f"The following tag columns have more than {MAX_TAG_LENGTH} characters: "
            f"{', '.join(map(str, self.wrong_value_columns))}."
        )


class InvalidRankingCategoryValue(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Ranking_Relevance_Labels_Value"

    def __init__(self, name: str) -> None:
        self.name = name

    def error_message(self) -> str:
        return (
            f"ranking relevance labels '{self.name}' column contains invalid value"
            f"make sure empty string is not present"
        )


class InvalidBoundingBoxesCoordinates(ValidationError, Exception):
    def __repr__(self) -> str:
        return "Invalid_Bounding_Boxes_Coordinates"

    def __init__(self, reason) -> None:
        self._check_valid_reason(reason)
        self.reason = reason

    @staticmethod
    def _check_valid_reason(reason):
        possible_reasons = (
            "none_boxes",
            "none_or_empty_box",
            "boxes_coordinates_wrong_format",
        )
        if reason not in possible_reasons:
            raise ValueError(
                f"Invalid reason {reason}. Possible reasons are: "
                f"{', '.join(possible_reasons)}."
            )

    def error_message(self) -> str:
        msg = "Invalid bounding boxes coordinates found. "
        if self.reason == "none_boxes":
            msg += (
                "Found at least one list of bounding boxes coordinates with NoneType. List of "
                "bounding boxes coordinates cannot be None, if you'd like to send no boxes, "
                "send an empty list"
            )
        elif self.reason == "none_or_empty_box":
            msg += (
                "Found at least one bounding box with None value or without coordinates. All "
                "bounding boxes in the list must contain its 4 coordinates"
            )
        elif self.reason == "boxes_coordinates_wrong_format":
            msg += (
                "Found at least one bound box's coordinates incorrectly formatted. Each "
                "bounding box's coordinates must be a collection of 4 positive floats "
                "representing the top-left & bottom-right corners of the box, in pixels"
            )
        return msg


class InvalidBoundingBoxesCategories(ValidationError, Exception):
    def __repr__(self) -> str:
        return "Invalid_Bounding_Boxes_Categories"

    def __init__(self, reason) -> None:
        self._check_valid_reason(reason)
        self.reason = reason

    @staticmethod
    def _check_valid_reason(reason):
        possible_reasons = (
            "none_category_list",
            "none_category",
        )
        if reason not in possible_reasons:
            raise ValueError(
                f"Invalid reason {reason}. Possible reasons are: "
                f"{', '.join(possible_reasons)}."
            )

    def error_message(self) -> str:
        msg = "Invalid bounding boxes categories found. "
        if self.reason == "none_category_list":
            msg += (
                "Found at least one list of bounding box categories with None value. Must send a "
                "list of categories, one category per bounding box."
            )
        elif self.reason == "none_category":
            msg += (
                "Found at least one category label with None value. Each bounding box category "
                "must be string. Empty strings are allowed"
            )
        return msg


class InvalidBoundingBoxesScores(ValidationError, Exception):
    def __repr__(self) -> str:
        return "Invalid_Bounding_Boxes_Scores"

    def __init__(self, reason) -> None:
        self._check_valid_reason(reason)
        self.reason = reason

    @staticmethod
    def _check_valid_reason(reason):
        possible_reasons = (
            "none_score_list",
            "scores_out_of_bounds",
        )
        if reason not in possible_reasons:
            raise ValueError(
                f"Invalid reason {reason}. Possible reasons are: "
                f"{', '.join(possible_reasons)}."
            )

    def error_message(self) -> str:
        msg = "Invalid bounding boxes scores found. "
        if self.reason == "none_score_list":
            msg += (
                "Found at least one list of bounding box scores with None value. This field is "
                "optional. If sent, you must send a confidence score per bounding box"
            )
        elif self.reason == "scores_out_of_bounds":
            msg += (
                "Found at least one confidence score out of bounds. "
                "Confidence scores must be between 0 and 1"
            )
        return msg


class InvalidPolygonCoordinates(ValidationError, Exception):
    def __repr__(self) -> str:
        return "Invalid_Polygon_Coordinates"

    def __init__(
        self, reason: str, coordinates: Optional[List[float]] = None
    ) -> None:
        self._check_valid_reason(reason)
        self.reason = reason
        self.coordinates = coordinates

    @staticmethod
    def _check_valid_reason(reason):
        possible_reasons = (
            "none_polygons",
            "none_or_empty_polygon",
            "polygon_coordinates_wrong_format",
            "polygon_coordinates_repeated_vertices",
            "polygon_coordinates_self_intersecting_vertices",
        )
        if reason not in possible_reasons:
            raise ValueError(
                f"Invalid reason {reason}. Possible reasons are: "
                f"{', '.join(possible_reasons)}."
            )

    def error_message(self) -> str:
        msg = "Invalid polygon coordinates found. "
        if self.reason == "none_polygons":
            msg += (
                "Found at least one list of polygon coordinates with NoneType. List of "
                "polygon coordinates cannot be None, if you'd like to send no coordinates, "
                "send an empty list"
            )
        elif self.reason == "none_or_empty_polygon":
            msg += (
                "Found at least one polygon with None value or without coordinates. All "
                "polygons in the list must contain its coordinates"
            )
        elif self.reason == "polygon_coordinates_wrong_format":
            msg += (
                "Found at least one polygon's coordinates incorrectly formatted. Each "
                "polygon's coordinates must be a collection of even number of positive floats "
                "representing the x and y coordinates of each point, in pixels. The following "
                f"coordinates are invalid: {self.coordinates}"
            )
        elif self.reason == "polygon_coordinates_repeated_vertices":
            msg += (
                "Found at least one polygon with repeated vertices. "
                "No polygon can have repeated vertices."
                f"The following coordinates are invalid: {self.coordinates}"
            )
        elif self.reason == "polygon_coordinates_self_intersecting_vertices":
            msg += (
                "Found at least one polygon with self-intersecting vertices. "
                "Each polygon must not have self-intersecting vertices."
                f"The following coordinates are invalid: {self.coordinates}"
            )
        return msg


class InvalidPolygonCategories(ValidationError, Exception):
    def __repr__(self) -> str:
        return "Invalid_Polygon_Categories"

    def __init__(self, reason) -> None:
        self._check_valid_reason(reason)
        self.reason = reason

    @staticmethod
    def _check_valid_reason(reason):
        possible_reasons = (
            "none_category_list",
            "none_category",
        )
        if reason not in possible_reasons:
            raise ValueError(
                f"Invalid reason {reason}. Possible reasons are: "
                f"{', '.join(possible_reasons)}."
            )

    def error_message(self) -> str:
        msg = "Invalid polygon categories found. "
        if self.reason == "none_category_list":
            msg += (
                "Found at least one list of polygon categories with None value. Must send a "
                "list of categories, one category per polygon."
            )
        elif self.reason == "none_category":
            msg += (
                "Found at least one category label with None value. Each polygon category "
                "must be string. Empty strings are allowed"
            )
        return msg


class InvalidPolygonScores(ValidationError, Exception):
    def __repr__(self) -> str:
        return "Invalid_Polygon_Scores"

    def __init__(self, reason) -> None:
        self._check_valid_reason(reason)
        self.reason = reason

    @staticmethod
    def _check_valid_reason(reason):
        possible_reasons = (
            "none_score_list",
            "scores_out_of_bounds",
        )
        if reason not in possible_reasons:
            raise ValueError(
                f"Invalid reason {reason}. Possible reasons are: "
                f"{', '.join(possible_reasons)}."
            )

    def error_message(self) -> str:
        msg = "Invalid polygon scores found. "
        if self.reason == "none_score_list":
            msg += (
                "Found at least one list of polygon scores with None value. This field is "
                "optional. If sent, you must send a confidence score per polygon"
            )
        elif self.reason == "scores_out_of_bounds":
            msg += (
                "Found at least one confidence score out of bounds. "
                "Confidence scores must be between 0 and 1"
            )
        return msg


class InvalidNumClassesMultiClassMap(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Num_classes_Multi_Class_Map"

    def __init__(
        self, dict_col_to_list_of_invalid_num_classes: Dict[str, List[str]]
    ) -> None:
        self.invalid_col_num_classes = dict_col_to_list_of_invalid_num_classes

    def error_message(self) -> str:
        err_msg = ""
        for (
            col,
            list_invalid_num_classes,
        ) in self.invalid_col_num_classes.items():
            num_invalid_num_classes = len(list_invalid_num_classes)
            set_invalid_num_classes = set(
                list_invalid_num_classes
            )  # to de-duplicate
            err_msg += (
                f"Multi-Class dictionary for the following column: {col} had {num_invalid_num_classes} rows"
                f"containing an invalid number of classes. The dictionary must contain at least 1 class"
                f"and at most {MAX_NUMBER_OF_MULTI_CLASS_CLASSES} classes. Found rows with the following "
                f"invalid number of classes: {log_a_list(list(set_invalid_num_classes), 'and')}\n"
            )
        return err_msg


class InvalidMultiClassClassNameLength(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Multi_Class_Class_Name_Length"

    def __init__(self, invalid_col_class_name: Dict[str, set]) -> None:
        self.invalid_col_class_name = invalid_col_class_name

    def error_message(self) -> str:
        err_msg = ""
        for col, class_names in self.invalid_col_class_name.items():
            # limit to 10
            class_names = (
                list(class_names)[:10]
                if len(class_names) > 10
                else list(class_names)
            )
            err_msg += (
                f"Found some invalid class names: {log_a_list(class_names, 'and')} in the {col} column. Class"
                f" names must have at least one character and less than {MAX_MULTI_CLASS_NAME_LENGTH}.\n"
            )
        return err_msg


class InvalidMultiClassPredScoreValue(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Multi_Class_Pred_Score_Value"

    def __init__(self, invalid_col_class_scores: Dict[str, set]) -> None:
        self.invalid_col_class_scores = invalid_col_class_scores

    def error_message(self) -> str:
        err_msg = ""
        for col, scores in self.invalid_col_class_scores.items():
            # limit to 10
            scores = list(scores)[:10] if len(scores) > 10 else list(scores)
            err_msg += (
                f"Found some invalid scores: {log_a_list(scores, 'and')} in the {col} column that was "
                "invalid. All scores (values in dictionary) must be between 0 and 1, inclusive. \n"
            )
        return err_msg


class InvalidMultiClassActScoreValue(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Multi_Class_Act_Score_Value"

    def __init__(self, name: str) -> None:
        self.name = name

    def error_message(self) -> str:
        return (
            f"Found at least one score in the '{self.name}' column that was invalid. "
            f"All scores (values) must be either 0 or 1."
        )


class InvalidMultiClassThresholdClasses(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Multi_Class_Threshold_Classes"

    def __init__(
        self, name: str, prediction_class_set: set, threshold_class_set: set
    ) -> None:
        self.name = name
        self.prediction_class_set = prediction_class_set
        self.threshold_class_set = threshold_class_set

    def error_message(self) -> str:
        return (
            "Multi-Class Prediction Scores and Threshold Scores Dictionaries must contain the same "
            f"classes. The following classes of the Prediction Scores Dictionary are not in the Threshold "
            f"Scores Dictionary: {self.prediction_class_set.difference(self.threshold_class_set)}"
            "\nThe following classes of the Threshold Scores Dictionary are not in the Prediction Scores "
            f"Dictionary: {self.threshold_class_set.difference(self.prediction_class_set)}\n"
        )


class InvalidAdditionalHeaders(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Additional_Headers"

    def __init__(self, invalid_headers: Iterable) -> None:
        self.invalid_header_names = invalid_headers

    def error_message(self) -> str:
        return (
            "Found invalid additional header, cannot use reserved headers named: "
            f"{', '.join(map(str, self.invalid_header_names))}."
        )


class InvalidRecord(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Record"

    def __init__(self, columns: List[str], indexes: List[int]) -> None:
        self.columns = columns
        self.indexes = indexes

    def error_message(self) -> str:
        return (
            f"Invalid column set full of null values in one or more rows.\n"
            f"\nProblematic Column Set:\n{log_a_list(self.columns, 'and')}\n"
            f"\nProblematic Rows:\n{log_a_list(self.indexes, join_word='and')}\n"
            "\nThis violates one of the following requirements:\n"
            " - If training environment: Prediction or actual columns cannot be all null.\n"
            " - If production environment: Prediction and actual columns cannot be all null.\n"
            " - If you are sending SHAP values, make sure not all your SHAP values are null "
            "in any given row.\n"
        )


class InvalidStringLength(Exception):
    def __init__(self, name: str, min_length: int, max_length: int) -> None:
        self.name = name
        self.min_length = min_length
        self.max_length = max_length

    def __repr__(self) -> str:
        return "Invalid_String_Length"

    def __str__(self) -> str:
        return self.error_message()

    def error_message(self) -> str:
        return f"{self.name} must be of length between {self.min_length} and {self.max_length} characters."
