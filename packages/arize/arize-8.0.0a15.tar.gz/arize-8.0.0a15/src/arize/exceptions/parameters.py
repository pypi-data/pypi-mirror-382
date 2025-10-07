from arize.constants.ml import MAX_NUMBER_OF_EMBEDDINGS
from arize.exceptions.base import ValidationError

# class MissingPredictionIdColumnForDelayedRecords(ValidationError):
#     def __repr__(self) -> str:
#         return "Missing_Prediction_Id_Column_For_Delayed_Records"
#
#     def __init__(self, has_actual_info, has_feature_importance_info) -> None:
#         self.has_actual_info = has_actual_info
#         self.has_feature_importance_info = has_feature_importance_info
#
#     def error_message(self) -> str:
#         actual = "actual" if self.has_actual_info else ""
#         feat_imp = (
#             "feature importance" if self.has_feature_importance_info else ""
#         )
#         if self.has_actual_info and self.has_feature_importance_info:
#             msg = " and ".join([actual, feat_imp])
#         else:
#             msg = "".join([actual, feat_imp])
#
#         return (
#             "Missing 'prediction_id_column_name'. While prediction id is optional for most cases, "
#             "it is required when sending delayed actuals, i.e. when sending actual or feature importances "
#             f"without predictions. In this case, {msg} information was found (without predictions). "
#             "To learn more about delayed joins, please see the docs at "
#             "https://docs.arize.com/arize/sending-data-guides/how-to-send-delayed-actuals"
#         )


# class MissingColumns(ValidationError):
#     def __repr__(self) -> str:
#         return "Missing_Columns"
#
#     def __init__(self, cols: Iterable) -> None:
#         self.missing_cols = set(cols)
#
#     def error_message(self) -> str:
#         return (
#             "The following columns are declared in the schema "
#             "but are not found in the dataframe: "
#             f"{', '.join(map(str, self.missing_cols))}."
#         )


# class MissingRequiredColumnsMetricsValidation(ValidationError):
#     """
#     This error is used only for model mapping validations.
#     """
#
#     def __repr__(self) -> str:
#         return "Missing_Columns_Required_By_Metrics_Validation"
#
#     def __init__(
#         self, model_type: ModelTypes, metrics: List[Metrics], cols: Iterable
#     ) -> None:
#         self.model_type = model_type
#         self.metrics = metrics
#         self.missing_cols = cols
#
#     def error_message(self) -> str:
#         return (
#             f"For logging data for a {self.model_type.name} model with support for metrics "
#             f"{', '.join(m.name for m in self.metrics)}, "
#             f"schema must include: {', '.join(map(str, self.missing_cols))}."
#         )


# class ReservedColumns(ValidationError):
#     def __repr__(self) -> str:
#         return "Reserved_Columns"
#
#     def __init__(self, cols: Iterable) -> None:
#         self.reserved_columns = cols
#
#     def error_message(self) -> str:
#         return (
#             "The following columns are reserved and can only be specified "
#             "in the proper fields of the schema: "
#             f"{', '.join(map(str, self.reserved_columns))}."
#         )


# class InvalidModelTypeAndMetricsCombination(ValidationError):
#     """
#     This error is used only for model mapping validations.
#     """
#
#     def __repr__(self) -> str:
#         return "Invalid_ModelType_And_Metrics_Combination"
#
#     def __init__(
#         self,
#         model_type: ModelTypes,
#         metrics: List[Metrics],
#         suggested_model_metric_combinations: List[List[str]],
#     ) -> None:
#         self.model_type = model_type
#         self.metrics = metrics
#         self.suggested_combinations = suggested_model_metric_combinations
#
#     def error_message(self) -> str:
#         valid_combos = ", or \n".join(
#             "[" + ", ".join(combo) + "]"
#             for combo in self.suggested_combinations
#         )
#         return (
#             f"Invalid combination of model type {self.model_type.name} and metrics: "
#             f"{', '.join(m.name for m in self.metrics)}. "
#             f"Valid Metric combinations for this model type:\n{valid_combos}.\n"
#         )


# class InvalidShapSuffix(ValidationError):
#     def __repr__(self) -> str:
#         return "Invalid_SHAP_Suffix"
#
#     def __init__(self, cols: Iterable) -> None:
#         self.invalid_column_names = cols
#
#     def error_message(self) -> str:
#         return (
#             "The following features or tags must not be named with a `_shap` suffix: "
#             f"{', '.join(map(str, self.invalid_column_names))}."
#         )


# class InvalidModelType(ValidationError):
#     def __repr__(self) -> str:
#         return "Invalid_Model_Type"
#
#     def error_message(self) -> str:
#         return (
#             "Model type not valid. Choose one of the following: "
#             f"{', '.join('ModelTypes.' + mt.name for mt in ModelTypes)}. "
#         )


# class InvalidEnvironment(ValidationError):
#     def __repr__(self) -> str:
#         return "Invalid_Environment"
#
#     def error_message(self) -> str:
#         return (
#             "Environment not valid. Choose one of the following: "
#             f"{', '.join('Environments.' + env.name for env in Environments)}. "
#         )


# class InvalidBatchId(ValidationError):
#     def __repr__(self) -> str:
#         return "Invalid_Batch_ID"
#
#     def error_message(self) -> str:
#         return "Batch ID must be a nonempty string if logging to validation environment."


class InvalidModelVersion(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Model_Version"

    def error_message(self) -> str:
        return "Model version must be a nonempty string."


# class InvalidModelId(ValidationError):
#     def __repr__(self) -> str:
#         return "Invalid_Model_ID"
#
#     def error_message(self) -> str:
#         return "Model ID must be a nonempty string."


class InvalidProjectName(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Project_Name"

    def error_message(self) -> str:
        return (
            "Project Name must be a nonempty string. "
            "If Model ID was used instead of Project Name, "
            "it must be a nonempty string."
        )


# class MissingPredActShap(ValidationError):
#     def __repr__(self) -> str:
#         return "Missing_Pred_or_Act_or_SHAP"
#
#     def error_message(self) -> str:
#         return (
#             "The schema must specify at least one of the following: "
#             "prediction label, actual label, or SHAP value column names"
#         )


# class MissingPreprodPredAct(ValidationError):
#     def __repr__(self) -> str:
#         return "Missing_Preproduction_Pred_and_Act"
#
#     def error_message(self) -> str:
#         return "For logging pre-production data, the schema must specify both "
#         "prediction and actual label columns."


# class MissingPreprodAct(ValidationError):
#     def __repr__(self) -> str:
#         return "Missing_Preproduction_Act"
#
#     def error_message(self) -> str:
#         return "For logging pre-production data, the schema must specify actual label column."


# class MissingPreprodPredActNumericAndCategorical(ValidationError):
#     def __repr__(self) -> str:
#         return "Missing_Preproduction_Pred_and_Act_Numeric_and_Categorical"
#
#     def error_message(self) -> str:
#         return (
#             "For logging pre-production data for a numeric or a categorical model, "
#             "the schema must specify both prediction and actual label or score columns."
#         )


# class MissingRequiredColumnsForRankingModel(ValidationError):
#     def __repr__(self) -> str:
#         return "Missing_Required_Columns_For_Ranking_Model"
#
#     def error_message(self) -> str:
#         return (
#             "For logging data for a ranking model, schema must specify: "
#             "prediction_group_id_column_name and rank_column_name"
#         )


# class MissingCVPredAct(ValidationError):
#     def __repr__(self) -> str:
#         return "Missing_CV_Prediction_or_Actual"
#
#     def __init__(self, environment: Environments):
#         self.environment = environment
#
#     def error_message(self) -> str:
#         if self.environment in (Environments.TRAINING, Environments.VALIDATION):
#             env = "pre-production"
#             opt = "and"
#         elif self.environment == Environments.PRODUCTION:
#             env = "production"
#             opt = "or"
#         else:
#             raise TypeError("Invalid environment")
#         return (
#             f"For logging {env} data for an Object Detection model,"
#             "the schema must specify one of: "
#             f"('object_detection_prediction_column_names' {opt} "
#             f"'object_detection_actual_column_names') "
#             f"or ('semantic_segmentation_prediction_column_names' {opt} "
#             f"'semantic_segmentation_actual_column_names') "
#             f"or ('instance_segmentation_prediction_column_names' {opt} "
#             f"'instance_segmentation_actual_column_names')"
#         )


# class MultipleCVPredAct(ValidationError):
#     def __repr__(self) -> str:
#         return "Multiple_CV_Prediction_or_Actual"
#
#     def __init__(self, environment: Environments):
#         self.environment = environment
#
#     def error_message(self) -> str:
#         return (
#             "The schema must only specify one of the following: "
#             "'object_detection_prediction_column_names'/'object_detection_actual_column_names'"
#             "'semantic_segmentation_prediction_column_names'/'semantic_segmentation_actual_column_names'"
#             "'instance_segmentation_prediction_column_names'/'instance_segmentation_actual_column_names'"
#         )


# class InvalidPredActCVColumnNamesForModelType(ValidationError):
#     def __repr__(self) -> str:
#         return "Invalid_CV_Prediction_or_Actual_Column_Names_for_Model_Type"
#
#     def __init__(
#         self,
#         invalid_model_type: ModelTypes,
#     ) -> None:
#         self.invalid_model_type = invalid_model_type
#
#     def error_message(self) -> str:
#         return (
#             f"Cannot use 'object_detection_prediction_column_names' or "
#             f"'object_detection_actual_column_names' or "
#             f"'semantic_segmentation_prediction_column_names' or "
#             f"'semantic_segmentation_actual_column_names' or "
#             f"'instance_segmentation_prediction_column_names' or "
#             f"'instance_segmentation_actual_column_names' for {self.invalid_model_type} model "
#             f"type. They are only allowed for ModelTypes.OBJECT_DETECTION models"
#         )


# class MissingReqPredActColumnNamesForMultiClass(ValidationError):
#     def __repr__(self) -> str:
#         return "Missing_Required_Prediction_or_Actual_Column_Names_for_Multi_Class_Model_Type"
#
#     def error_message(self) -> str:
#         return (
#             "For logging data for a multi class model, schema must specify: "
#             "prediction_scores_column_name and/or actual_score_column_name. "
#             "Optionally, you may include multi_class_threshold_scores_column_name"
#             " (must include prediction_scores_column_name)"
#         )


# class InvalidPredActColumnNamesForModelType(ValidationError):
#     def __repr__(self) -> str:
#         return "Invalid_Prediction_or_Actual_Column_Names_for_Model_Type"
#
#     def __init__(
#         self,
#         invalid_model_type: ModelTypes,
#         allowed_fields: List[str],
#         wrong_columns: List[str],
#     ) -> None:
#         self.invalid_model_type = invalid_model_type
#         self.allowed_fields = allowed_fields
#         self.wrong_columns = wrong_columns
#
#     def error_message(self) -> str:
#         allowed_col_msg = ""
#         if self.allowed_fields is not None:
#             allowed_col_msg = f" Allowed Schema fields are {log_a_list(self.allowed_fields, 'and')}"
#         return (
#             f"Invalid Schema fields for {self.invalid_model_type} model type. {allowed_col_msg}"
#             "The following columns of your dataframe are sent as an invalid schema field: "
#             f"{log_a_list(self.wrong_columns, 'and')}"
#         )


# class DuplicateColumnsInDataframe(ValidationError):
#     def __repr__(self) -> str:
#         return "Duplicate_Columns_In_Dataframe"
#
#     def __init__(self, cols: Iterable) -> None:
#         self.duplicate_cols = cols
#
#     def error_message(self) -> str:
#         return (
#             "The following columns are present in the schema and have duplicates in the dataframe: "
#             f"{self.duplicate_cols}. "
#         )


class InvalidNumberOfEmbeddings(ValidationError):
    def __repr__(self) -> str:
        return "Invalid_Number_Of_Embeddings"

    def __init__(self, number_of_embeddings: int) -> None:
        self.number_of_embeddings = number_of_embeddings

    def error_message(self) -> str:
        return (
            f"The schema contains {self.number_of_embeddings} different embeddings when a maximum of "
            f"{MAX_NUMBER_OF_EMBEDDINGS} is allowed."
        )


class InvalidValueType(Exception):
    def __init__(
        self,
        value_name: str,
        value: bool | int | float | str,
        correct_type: str,
    ) -> None:
        self.value_name = value_name
        self.value = value
        self.correct_type = correct_type

    def __repr__(self) -> str:
        return "Invalid_Value_Type"

    def __str__(self) -> str:
        return self.error_message()

    def error_message(self) -> str:
        return (
            f"{self.value_name} with value {self.value} is of type {type(self.value).__name__}, "
            f"but expected {self.correct_type}"
        )
