# type: ignore[pb2]
from typing import Dict, Tuple

from arize.constants.ml import MAX_PREDICTION_ID_LEN, MIN_PREDICTION_ID_LEN
from arize.exceptions.parameters import (
    InvalidValueType,
)
from arize.types import (
    CATEGORICAL_MODEL_TYPES,
    NUMERIC_MODEL_TYPES,
    ActualLabelTypes,
    Embedding,
    Environments,
    InstanceSegmentationActualLabel,
    InstanceSegmentationPredictionLabel,
    ModelTypes,
    MultiClassActualLabel,
    MultiClassPredictionLabel,
    ObjectDetectionLabel,
    PredictionIDType,
    PredictionLabelTypes,
    RankingActualLabel,
    RankingPredictionLabel,
    SemanticSegmentationLabel,
)


def validate_label(
    prediction_or_actual: str,
    model_type: ModelTypes,
    label: str
    | bool
    | int
    | float
    | Tuple[str | bool, float]
    | ObjectDetectionLabel
    | RankingPredictionLabel
    | RankingActualLabel
    | SemanticSegmentationLabel
    | InstanceSegmentationPredictionLabel
    | InstanceSegmentationActualLabel
    | MultiClassPredictionLabel
    | MultiClassActualLabel,
    embedding_features: Dict[str, Embedding],
):
    if model_type in NUMERIC_MODEL_TYPES:
        _validate_numeric_label(model_type, label)
    elif model_type in CATEGORICAL_MODEL_TYPES:
        _validate_categorical_label(model_type, label)
    elif model_type == ModelTypes.OBJECT_DETECTION:
        _validate_cv_label(prediction_or_actual, label, embedding_features)
    elif model_type == ModelTypes.RANKING:
        _validate_ranking_label(label)
    elif model_type == ModelTypes.GENERATIVE_LLM:
        _validate_generative_llm_label(label)
    elif model_type == ModelTypes.MULTI_CLASS:
        _validate_multi_class_label(label)
    else:
        raise InvalidValueType(
            "model_type", model_type, "arize.utils.ModelTypes"
        )


def _validate_numeric_label(
    model_type: ModelTypes,
    label: str | bool | int | float | Tuple[str | bool, float],
):
    if not isinstance(label, (float, int)):
        raise InvalidValueType(
            f"label {label}",
            label,
            f"either float or int for model_type {model_type}",
        )


def _validate_categorical_label(
    model_type: ModelTypes,
    label: str | bool | int | float | Tuple[str | bool, float],
):
    is_valid = isinstance(label, (str, bool, int, float)) or (
        isinstance(label, tuple)
        and isinstance(label[0], (str, bool))
        and isinstance(label[1], float)
    )
    if not is_valid:
        raise InvalidValueType(
            f"label {label}",
            label,
            f"one of: bool, int, float, str or Tuple[str, float] for model type {model_type}",
        )


def _validate_cv_label(
    prediction_or_actual: str,
    label: ObjectDetectionLabel
    | SemanticSegmentationLabel
    | InstanceSegmentationPredictionLabel
    | InstanceSegmentationActualLabel,
    embedding_features: Dict[str, Embedding],
):
    if (
        not isinstance(label, ObjectDetectionLabel)
        and not isinstance(label, SemanticSegmentationLabel)
        and not isinstance(label, InstanceSegmentationPredictionLabel)
        and not isinstance(label, InstanceSegmentationActualLabel)
    ):
        raise InvalidValueType(
            f"label {label}",
            label,
            "one of: ObjectDetectionLabel, SemanticSegmentationLabel, InstanceSegmentationPredictionLabel, "
            f"or InstanceSegmentationActualLabel for model type {ModelTypes.OBJECT_DETECTION}",
        )
    if embedding_features is None:
        raise ValueError(
            f"Cannot use {type(label)} without an embedding feature"
        )
    if len(embedding_features.keys()) != 1:
        raise ValueError(
            f"{type(label)} must be sent with exactly one embedding feature"
        )
    if isinstance(label, ObjectDetectionLabel):
        label.validate(prediction_or_actual=prediction_or_actual)
    else:
        label.validate()


def _validate_ranking_label(
    label: RankingPredictionLabel | RankingActualLabel,
):
    if not isinstance(label, (RankingPredictionLabel, RankingActualLabel)):
        raise InvalidValueType(
            f"label {label}",
            label,
            f"RankingPredictionLabel or RankingActualLabel for model type {ModelTypes.RANKING}",
        )
    label.validate()


def _validate_generative_llm_label(
    label: str | bool | int | float,
):
    is_valid = isinstance(label, (str, bool, int, float))
    if not is_valid:
        raise InvalidValueType(
            f"label {label}",
            label,
            f"one of: bool, int, float, str for model type {ModelTypes.GENERATIVE_LLM}",
        )


def _validate_multi_class_label(
    label: MultiClassPredictionLabel | MultiClassActualLabel,
):
    if not isinstance(
        label, (MultiClassPredictionLabel, MultiClassActualLabel)
    ):
        raise InvalidValueType(
            f"label {label}",
            label,
            f"MultiClassPredictionLabel or MultiClassActualLabel for model type {ModelTypes.MULTI_CLASS}",
        )
    label.validate()


def validate_and_convert_prediction_id(
    prediction_id: PredictionIDType | None,
    environment: Environments,
    prediction_label: PredictionLabelTypes | None = None,
    actual_label: ActualLabelTypes | None = None,
    shap_values: Dict[str, float] | None = None,
) -> str:
    # If the user does not provide prediction id
    if prediction_id:
        # If prediction id is given by user, convert it to string and validate length
        return _convert_prediction_id(prediction_id)

    # delayed records have actual information but not prediction information
    is_delayed_record = prediction_label is None and (
        actual_label is not None or shap_values is not None
    )
    # Pre-production environment does not need prediction id
    # Production environment needs prediction id for delayed record, since joins are needed
    if is_delayed_record and environment == Environments.PRODUCTION:
        raise ValueError(
            "prediction_id value cannot be None for delayed records, i.e., records ",
            "without prediction_label and with either actual_label or shap_values",
        )
    # Prediction ids are optional for: pre-production records and
    # production records that are not delayed records, they are generated
    # server-side
    return ""


def _convert_prediction_id(
    prediction_id: PredictionIDType,
) -> str:
    if not isinstance(prediction_id, str):
        try:
            prediction_id = str(
                prediction_id
            ).strip()  # strip ensures we don't receive whitespaces as part of the prediction id
        except Exception as e:
            raise ValueError(
                f"prediction_id value {prediction_id} must be convertible to a string"
            ) from e

    if len(prediction_id) not in range(
        MIN_PREDICTION_ID_LEN, MAX_PREDICTION_ID_LEN + 1
    ):
        raise ValueError(
            f"The string length of prediction_id {prediction_id} must be between {MIN_PREDICTION_ID_LEN} "
            f"and {MAX_PREDICTION_ID_LEN}"
        )
    return prediction_id
