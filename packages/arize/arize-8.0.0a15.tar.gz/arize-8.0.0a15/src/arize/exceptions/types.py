from collections.abc import Iterable
from typing import List

from arize.constants.ml import (
    MAX_EMBEDDING_DIMENSIONALITY,
    MAX_RAW_DATA_CHARACTERS,
)
from arize.exceptions.base import ValidationError


class InvalidType(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Type"

    def __init__(
        self, name: str, expected_types: List[str], found_data_type: str
    ) -> None:
        self.name = name
        self.expected_types = expected_types
        self.found_data_type = found_data_type

    def error_message(self) -> str:
        type_list = (
            self.expected_types[0]
            if len(self.expected_types) == 1
            else f"{', '.join(map(str, self.expected_types[:-1]))} or {self.expected_types[-1]}"
        )
        return (
            f"{self.name} must be of type {type_list} but found {self.found_data_type}. "
            "Warning: if you are sending a column with integers, presence of a null "
            "value can convert the data type of the entire column to float."
        )


class InvalidTypeColumns(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Type_Columns"

    def __init__(
        self, wrong_type_columns: List[str], expected_types: List[str]
    ) -> None:
        self.wrong_type_columns = wrong_type_columns
        self.expected_types = expected_types

    def error_message(self) -> str:
        col_list = (
            self.wrong_type_columns[0]
            if len(self.wrong_type_columns) == 1
            else f"{', '.join(self.wrong_type_columns[:-1])}, and {self.wrong_type_columns[-1]}"
        )
        type_list = (
            self.expected_types[0]
            if len(self.expected_types) == 1
            else f"{', '.join(map(str, self.expected_types[:-1]))} or {self.expected_types[-1]}"
        )
        return f"The column(s) {col_list}; must be of type {type_list}."


class InvalidTypeFeatures(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Type_Features"

    def __init__(self, cols: Iterable, expected_types: List[str]) -> None:
        self.wrong_type_columns = cols
        self.expected_types = expected_types

    def error_message(self) -> str:
        type_list = (
            self.expected_types[0]
            if len(self.expected_types) == 1
            else f"{', '.join(map(str, self.expected_types[:-1]))} or {self.expected_types[-1]}"
        )
        return (
            f"Features must be of type {type_list}. "
            "The following feature columns have unrecognized data types: "
            f"{', '.join(map(str, self.wrong_type_columns))}."
        )


class InvalidFieldTypePromptTemplates(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Input_Type_Prompt_Templates"

    def error_message(self) -> str:
        return "prompt_template_column_names must be of type PromptTemplateColumnNames"


class InvalidFieldTypeLlmConfig(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Input_Type_LLM_Config"

    def error_message(self) -> str:
        return "llm_config_column_names must be of type LLMConfigColumnNames"


class InvalidTypeTags(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Type_Tags"

    def __init__(self, cols: Iterable, expected_types: List[str]) -> None:
        self.wrong_type_columns = cols
        self.expected_types = expected_types

    def error_message(self) -> str:
        type_list = (
            self.expected_types[0]
            if len(self.expected_types) == 1
            else f"{', '.join(map(str, self.expected_types[:-1]))} or {self.expected_types[-1]}"
        )
        return (
            f"Tags must be of type {type_list}. "
            "The following tag columns have unrecognized data types: "
            f"{', '.join(map(str, self.wrong_type_columns))}."
        )


class InvalidValueEmbeddingVectorDimensionality(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Value_Embedding_Vector_Dimensionality"

    def __init__(self, dim_1_cols: List[str], high_dim_cols: List[str]) -> None:
        self.dim_1_cols = dim_1_cols
        self.high_dim_cols = high_dim_cols

    def error_message(self) -> str:
        msg = (
            "Embedding vectors cannot have length (dimensionality) of 1 or higher "
            f"than {MAX_EMBEDDING_DIMENSIONALITY}. "
        )
        if self.dim_1_cols:
            msg += f"The following columns have dimensionality of 1: {','.join(self.dim_1_cols)}. "
        if self.high_dim_cols:
            msg += (
                f"The following columns have dimensionality greater than {MAX_EMBEDDING_DIMENSIONALITY}: "
                f"{','.join(self.high_dim_cols)}. "
            )

        return msg


class InvalidValueEmbeddingRawDataTooLong(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Value_Embedding_Raw_Data_Too_Long"

    def __init__(self, cols: Iterable) -> None:
        self.invalid_cols = cols

    def error_message(self) -> str:
        return (
            f"Embedding raw data cannot have more than {MAX_RAW_DATA_CHARACTERS} characters. "
            "The following columns do not satisfy this condition: "
            f"{', '.join(map(str, self.invalid_cols))}."
        )


class InvalidTypeShapValues(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Type_SHAP_Values"

    def __init__(self, cols: Iterable, expected_types: List[str]) -> None:
        self.wrong_type_columns = cols
        self.expected_types = expected_types

    def error_message(self) -> str:
        type_list = (
            self.expected_types[0]
            if len(self.expected_types) == 1
            else f"{', '.join(map(str, self.expected_types[:-1]))} or {self.expected_types[-1]}"
        )
        return (
            f"SHAP values must be of type {type_list}. "
            "The following SHAP columns have unrecognized data types: "
            f"{', '.join(map(str, self.wrong_type_columns))}."
        )
