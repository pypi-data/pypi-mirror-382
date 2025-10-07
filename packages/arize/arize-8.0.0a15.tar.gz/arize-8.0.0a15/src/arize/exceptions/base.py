from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import List

INVALID_ARROW_CONVERSION_MSG = (
    "The dataframe needs to convert to pyarrow but has failed to do so. "
    "There may be unrecognized data types in the dataframe. "
    "Another reason may be that a column in the dataframe has a mix of strings and "
    "numbers, in which case you may want to convert the strings in that column to NaN. "
)


class ValidationError(Exception, ABC):
    def __str__(self) -> str:
        return self.error_message()

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def error_message(self) -> str:
        pass


class ValidationFailure(Exception):
    def __init__(self, errors: List[ValidationError]) -> None:
        self.errors = errors


# ----------------------
# Minimum required checks
# ----------------------
# class InvalidColumnNameEmptyString(ValidationError):
#     def __repr__(self) -> str:
#         return "Invalid_Column_Name_Empty_String"
#
#     def error_message(self) -> str:
#         return (
#             "Empty column name found: ''. The schema cannot point to columns in the "
#             "dataframe denoted by an empty string. You can see the columns used in the "
#             "schema by running schema.get_used_columns()"
#         )


class InvalidFieldTypeConversion(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Input_Type_Conversion"

    def __init__(self, fields: Iterable, type: str) -> None:
        self.fields = fields
        self.type = type

    def error_message(self) -> str:
        return (
            f"The following fields must be convertible to {self.type}: "
            f"{', '.join(map(str, self.fields))}."
        )


# class InvalidFieldTypeEmbeddingFeatures(ValidationError):
#     def __repr__(self) -> str:
#         return "Invalid_Input_Type_Embedding_Features"
#
#     def __init__(self) -> None:
#         pass
#
#     def error_message(self) -> str:
#         return (
#             "schema.embedding_feature_column_names should be a dictionary mapping strings "
#             "to EmbeddingColumnNames objects"
#         )


# class InvalidFieldTypePromptResponse(ValidationError):
#     def __repr__(self) -> str:
#         return "Invalid_Input_Type_Prompt_Response"
#
#     def __init__(self, name: str) -> None:
#         self.name = name
#
#     def error_message(self) -> str:
#         return f"'{self.name}' must be of type str or EmbeddingColumnNames"


class InvalidDataFrameIndex(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Index"

    def error_message(self) -> str:
        return (
            "The index of the dataframe is invalid; "
            "reset the index by using df.reset_index(drop=True, inplace=True)"
        )


# class InvalidSchemaType(ValidationError):
#     def __repr__(self) -> str:
#         return "Invalid_Schema_Type"
#
#     def __init__(self, schema_type: str, environment: Environments) -> None:
#         self.schema_type = schema_type
#         self.environment = environment
#
#     def error_message(self) -> str:
#         return f"Cannot use a {self.schema_type} for a model with environment: {self.environment}"
