# type: ignore[pb2]
from __future__ import annotations

import copy
import logging
import time
from typing import TYPE_CHECKING, Dict, List, Tuple

from arize._lazy import require
from arize.constants.ml import (
    LLM_RUN_METADATA_PROMPT_TOKEN_COUNT_TAG_NAME,
    LLM_RUN_METADATA_RESPONSE_LATENCY_MS_TAG_NAME,
    LLM_RUN_METADATA_RESPONSE_TOKEN_COUNT_TAG_NAME,
    LLM_RUN_METADATA_TOTAL_TOKEN_COUNT_TAG_NAME,
    MAX_FUTURE_YEARS_FROM_CURRENT_TIME,
    MAX_NUMBER_OF_EMBEDDINGS,
    MAX_PAST_YEARS_FROM_CURRENT_TIME,
    MAX_TAG_LENGTH,
    MAX_TAG_LENGTH_TRUNCATION,
    RESERVED_TAG_COLS,
)
from arize.exceptions.base import (
    INVALID_ARROW_CONVERSION_MSG,
    ValidationFailure,
)
from arize.exceptions.models import MissingModelNameError
from arize.exceptions.parameters import (
    InvalidNumberOfEmbeddings,
    InvalidValueType,
)
from arize.exceptions.spaces import MissingSpaceIDError
from arize.logging import get_truncation_warning_message
from arize.models.bounded_executor import BoundedExecutor
from arize.models.casting import cast_dictionary, cast_typed_columns
from arize.models.stream_validation import (
    validate_and_convert_prediction_id,
    validate_label,
)
from arize.types import (
    CATEGORICAL_MODEL_TYPES,
    NUMERIC_MODEL_TYPES,
    ActualLabelTypes,
    BaseSchema,
    CorpusSchema,
    Embedding,
    Environments,
    LLMRunMetadata,
    Metrics,
    ModelTypes,
    PredictionIDType,
    PredictionLabelTypes,
    Schema,
    SimilaritySearchParams,
    TypedValue,
    convert_element,
    is_list_of,
)

if TYPE_CHECKING:
    import concurrent.futures as cf
    from datetime import datetime

    import pandas as pd
    import requests
    from requests_futures.sessions import FuturesSession

    from arize._generated.protocol.rec import public_pb2 as pb2
    from arize.config import SDKConfiguration
    from arize.types import (
        EmbeddingColumnNames,
        Schema,
    )


logger = logging.getLogger(__name__)

_STREAM_DEPS = (
    "requests_futures",
    "google.protobuf",
)
_STREAM_EXTRA = "ml-stream"

_BATCH_DEPS = (
    "pandas",
    "google.protobuf",
    "pyarrow",
    "requests",
    "tqdm",
)
_BATCH_EXTRA = "ml-batch"
_MIMIC_DEPS = (
    "interpret_community.mimic",
    "sklearn.preprocessing",
)
_MIMIC_EXTRA = "mimic-explainer"


class MLModelsClient:
    def __init__(self, sdk_config: SDKConfiguration):
        self._sdk_config = sdk_config

        # internal cache for the futures session
        self._session: FuturesSession | None = None

    def log_stream(
        self,
        space_id: str,
        model_name: str,
        model_type: ModelTypes,
        environment: Environments,
        model_version: str | None = None,
        prediction_id: PredictionIDType | None = None,
        prediction_timestamp: int | None = None,
        prediction_label: PredictionLabelTypes | None = None,
        actual_label: ActualLabelTypes | None = None,
        features: Dict[str, str | bool | float | int | List[str] | TypedValue]
        | None = None,
        embedding_features: Dict[str, Embedding] | None = None,
        shap_values: Dict[str, float] | None = None,
        tags: Dict[str, str | bool | float | int | TypedValue] | None = None,
        batch_id: str | None = None,
        prompt: str | Embedding | None = None,
        response: str | Embedding | None = None,
        prompt_template: str | None = None,
        prompt_template_version: str | None = None,
        llm_model_name: str | None = None,
        llm_params: Dict[str, str | bool | float | int] | None = None,
        llm_run_metadata: LLMRunMetadata | None = None,
        timeout: float | None = None,
    ) -> cf.Future:
        require(_STREAM_EXTRA, _STREAM_DEPS)
        from arize._generated.protocol.rec import public_pb2 as pb2
        from arize.models.proto import (
            get_pb_dictionary,
            get_pb_label,
            get_pb_timestamp,
        )

        if model_type == ModelTypes.GENERATIVE_LLM:
            raise ValueError(
                "Wrong model type found: GENERATIVE_LLM. To send LLM data to Arize, "
                "use the spans module `arize_client.spans` or OTEL tracing"
            )

        # This method requires a space_id and project_name
        if not space_id:
            raise MissingSpaceIDError()
        if not model_name:
            raise MissingModelNameError()

        # Validate batch_id
        if environment == Environments.VALIDATION and (
            batch_id is None
            or not isinstance(batch_id, str)
            or len(batch_id.strip()) == 0
        ):
            raise ValueError(
                "Batch ID must be a nonempty string if logging to validation environment."
            )

        # Convert & Validate prediction_id
        prediction_id = validate_and_convert_prediction_id(
            prediction_id,
            environment,
            prediction_label,
            actual_label,
            shap_values,
        )

        # Cast feature & tag values
        if features:
            features = cast_dictionary(features)
            # Defensive check
            if not isinstance(features, dict):
                raise InvalidValueType("features", features, "dict")

            for feat_name, feat_value in features.items():
                _validate_mapping_key(feat_name, "features")
                if is_list_of(feat_value, str):
                    continue
                else:
                    val = convert_element(feat_value)
                    if val is not None and not isinstance(
                        val, (str, bool, float, int)
                    ):
                        raise InvalidValueType(
                            f"feature '{feat_name}'",
                            feat_value,
                            "one of: bool, int, float, str",
                        )

        # Validate embedding_features type
        if embedding_features:
            if not isinstance(embedding_features, dict):
                raise InvalidValueType(
                    "embedding_features", embedding_features, "dict"
                )
            if len(embedding_features) > MAX_NUMBER_OF_EMBEDDINGS:
                raise InvalidNumberOfEmbeddings(len(embedding_features))
            if (
                model_type == ModelTypes.OBJECT_DETECTION
                and len(embedding_features.keys()) > 1
            ):
                # Check that there is only 1 embedding feature for OD model types
                raise ValueError(
                    "Object Detection models only support one embedding feature"
                )
            for emb_name, emb_obj in embedding_features.items():
                _validate_mapping_key(emb_name, "embedding features")
                # Must verify embedding type
                if not isinstance(emb_obj, Embedding):
                    raise InvalidValueType(
                        f"embedding feature '{emb_name}'", emb_obj, "Embedding"
                    )
                emb_obj.validate(emb_name)
        if tags:
            tags = cast_dictionary(tags)
            # Defensive check
            if not isinstance(tags, dict):
                raise InvalidValueType("tags", tags, "dict")
            wrong_tags = [
                tag_name for tag_name in tags if tag_name in RESERVED_TAG_COLS
            ]
            if wrong_tags:
                raise KeyError(
                    f"The following tag names are not allowed as they are reserved: {wrong_tags}"
                )
            for tag_name, tag_value in tags.items():
                _validate_mapping_key(tag_name, "tags")
                val = convert_element(tag_value)
                if val is not None and not isinstance(
                    val, (str, bool, float, int)
                ):
                    raise InvalidValueType(
                        f"tag '{tag_name}'",
                        tag_value,
                        "one of: bool, int, float, str",
                    )
                if isinstance(tag_name, str) and tag_name.endswith("_shap"):
                    raise ValueError(
                        f"tag {tag_name} must not be named with a `_shap` suffix"
                    )
                if len(str(val)) > MAX_TAG_LENGTH:
                    raise ValueError(
                        f"The number of characters for each tag must be less than or equal to "
                        f"{MAX_TAG_LENGTH}. The tag {tag_name} with value {tag_value} has "
                        f"{len(str(val))} characters."
                    )
                elif len(str(val)) > MAX_TAG_LENGTH_TRUNCATION:
                    logger.warning(
                        get_truncation_warning_message(
                            "tags", MAX_TAG_LENGTH_TRUNCATION
                        )
                    )

        # Check the timestamp present on the event
        if prediction_timestamp is not None:
            if not isinstance(prediction_timestamp, int):
                raise InvalidValueType(
                    "prediction_timestamp", prediction_timestamp, "int"
                )
            # Send warning if prediction is sent with future timestamp
            now = int(time.time())
            if prediction_timestamp > now:
                logger.warning(
                    "Caution when sending a prediction with future timestamp."
                    "Arize only stores 2 years worth of data. For example, if you sent a prediction "
                    "to Arize from 1.5 years ago, and now send a prediction with timestamp of a year in "
                    "the future, the oldest 0.5 years will be dropped to maintain the 2 years worth of data "
                    "requirement."
                )
            if not _is_timestamp_in_range(now, prediction_timestamp):
                raise ValueError(
                    f"prediction_timestamp: {prediction_timestamp} is out of range."
                    f"Prediction timestamps must be within {MAX_FUTURE_YEARS_FROM_CURRENT_TIME} year in the "
                    f"future and {MAX_PAST_YEARS_FROM_CURRENT_TIME} years in the past from the current time."
                )

        # Construct the prediction
        p = None
        if prediction_label is not None:
            if model_version is not None and not isinstance(model_version, str):
                raise InvalidValueType("model_version", model_version, "str")
            validate_label(
                prediction_or_actual="prediction",
                model_type=model_type,
                label=convert_element(prediction_label),
                embedding_features=embedding_features,
            )
            p = pb2.Prediction(
                prediction_label=get_pb_label(
                    prediction_or_actual="prediction",
                    value=prediction_label,
                    model_type=model_type,
                ),
                model_version=model_version,
            )
            if features is not None:
                converted_feats = get_pb_dictionary(features)
                feats = pb2.Prediction(features=converted_feats)
                p.MergeFrom(feats)

            if embedding_features or prompt or response:
                # NOTE: Deep copy is necessary to avoid side effects on the original input dictionary
                combined_embedding_features = (
                    {k: v for k, v in embedding_features.items()}
                    if embedding_features
                    else {}
                )
                # Map prompt as embedding features for generative models
                if prompt is not None:
                    combined_embedding_features.update({"prompt": prompt})
                # Map response as embedding features for generative models
                if response is not None:
                    combined_embedding_features.update({"response": response})
                converted_embedding_feats = get_pb_dictionary(
                    combined_embedding_features
                )
                embedding_feats = pb2.Prediction(
                    features=converted_embedding_feats
                )
                p.MergeFrom(embedding_feats)

            if tags or llm_run_metadata:
                joined_tags = copy.deepcopy(tags)
                if llm_run_metadata:
                    if llm_run_metadata.total_token_count is not None:
                        joined_tags[
                            LLM_RUN_METADATA_TOTAL_TOKEN_COUNT_TAG_NAME
                        ] = llm_run_metadata.total_token_count
                    if llm_run_metadata.prompt_token_count is not None:
                        joined_tags[
                            LLM_RUN_METADATA_PROMPT_TOKEN_COUNT_TAG_NAME
                        ] = llm_run_metadata.prompt_token_count
                    if llm_run_metadata.response_token_count is not None:
                        joined_tags[
                            LLM_RUN_METADATA_RESPONSE_TOKEN_COUNT_TAG_NAME
                        ] = llm_run_metadata.response_token_count
                    if llm_run_metadata.response_latency_ms is not None:
                        joined_tags[
                            LLM_RUN_METADATA_RESPONSE_LATENCY_MS_TAG_NAME
                        ] = llm_run_metadata.response_latency_ms
                converted_tags = get_pb_dictionary(joined_tags)
                tgs = pb2.Prediction(tags=converted_tags)
                p.MergeFrom(tgs)

            if (
                prompt_template
                or prompt_template_version
                or llm_model_name
                or llm_params
            ):
                llm_fields = pb2.LLMFields(
                    prompt_template=prompt_template or "",
                    prompt_template_name=prompt_template_version or "",
                    llm_model_name=llm_model_name or "",
                    llm_params=get_pb_dictionary(llm_params),
                )
                p.MergeFrom(pb2.Prediction(llm_fields=llm_fields))

            if prediction_timestamp is not None:
                p.timestamp.MergeFrom(get_pb_timestamp(prediction_timestamp))

        # Validate and construct the optional actual
        is_latent_tags = prediction_label is None and tags is not None
        a = None
        if actual_label or is_latent_tags:
            a = pb2.Actual()
            if actual_label is not None:
                validate_label(
                    prediction_or_actual="actual",
                    model_type=model_type,
                    label=convert_element(actual_label),
                    embedding_features=embedding_features,
                )
                a.MergeFrom(
                    pb2.Actual(
                        actual_label=get_pb_label(
                            prediction_or_actual="actual",
                            value=actual_label,
                            model_type=model_type,
                        )
                    )
                )
            # Added to support delayed tags on actuals.
            if tags is not None:
                converted_tags = get_pb_dictionary(tags)
                a.MergeFrom(pb2.Actual(tags=converted_tags))

        # Validate and construct the optional feature importances
        fi = None
        if shap_values is not None and bool(shap_values):
            for k, v in shap_values.items():
                if not isinstance(convert_element(v), float):
                    raise InvalidValueType(f"feature '{k}'", v, "float")
                if isinstance(k, str) and k.endswith("_shap"):
                    raise ValueError(
                        f"feature {k} must not be named with a `_shap` suffix"
                    )
            fi = pb2.FeatureImportances(feature_importances=shap_values)

        if p is None and a is None and fi is None:
            raise ValueError(
                "must provide at least one of prediction_label, actual_label, tags, or shap_values"
            )

        env_params = None
        if environment == Environments.TRAINING:
            if p is None or a is None:
                raise ValueError(
                    "Training records must have both Prediction and Actual"
                )
            env_params = pb2.Record.EnvironmentParams(
                training=pb2.Record.EnvironmentParams.Training()
            )
        elif environment == Environments.VALIDATION:
            if p is None or a is None:
                raise ValueError(
                    "Validation records must have both Prediction and Actual"
                )
            env_params = pb2.Record.EnvironmentParams(
                validation=pb2.Record.EnvironmentParams.Validation(
                    batch_id=batch_id
                )
            )
        elif environment == Environments.PRODUCTION:
            env_params = pb2.Record.EnvironmentParams(
                production=pb2.Record.EnvironmentParams.Production()
            )

        rec = pb2.Record(
            # We don't pass the deprecated space key
            # as part of the public record, we pass the space ID in the header
            model_id=model_name,
            prediction_id=prediction_id,
            prediction=p,
            actual=a,
            feature_importances=fi,
            environment_params=env_params,
        )
        headers = self._sdk_config.headers_grpc
        headers.update(
            {
                "Grpc-Metadata-arize-space-id": space_id,
                "Grpc-Metadata-arize-interface": "stream",
            }
        )
        return self._post(
            record=rec,
            headers=headers,
            timeout=timeout,
            indexes=None,
        )

    # TODO(Kiko): Handle sync argument
    def log_batch(
        self,
        space_id: str,
        model_name: str,
        model_type: ModelTypes,
        dataframe: pd.DataFrame,
        schema: BaseSchema,
        environment: Environments,
        model_version: str = "",
        batch_id: str = "",
        validate: bool = True,
        metrics_validation: List[Metrics] | None = None,
        surrogate_explainability: bool = False,
        timeout: float | None = None,
        tmp_dir: str = "",
        sync: bool = False,
    ) -> requests.Response:
        require(_BATCH_EXTRA, _BATCH_DEPS)
        import pandas.api.types as ptypes
        import pyarrow as pa

        from arize.models.batch_validation.validator import Validator
        from arize.utils.arrow import post_arrow_table
        from arize.utils.dataframe import remove_extraneous_columns

        # This method requires a space_id and project_name
        if not space_id:
            raise MissingSpaceIDError()
        if not model_name:
            raise MissingModelNameError()

        # Deep copy the schema since we might modify it to add certain columns and don't
        # want to cause side effects
        schema = copy.deepcopy(schema)

        if model_type == ModelTypes.GENERATIVE_LLM:
            raise ValueError(
                "Wrong model type found: GENERATIVE_LLM. To send LLM data to Arize, "
                "use the spans module `arize_client.spans` or OTEL tracing"
            )

        # If typed columns are specified in the schema,
        # apply casting and return new copies of the dataframe + schema.
        # All downstream validations are kept the same.
        # note: we don't do any casting for Corpus schemas.
        if isinstance(schema, Schema) and schema.has_typed_columns():
            # The pandas nullable string column type (StringDType) is still considered experimental
            # and is unavailable before pandas 1.0.0.
            # Thus we can only offer this functionality with pandas>=1.0.0.
            try:
                dataframe, schema = cast_typed_columns(dataframe, schema)
            except Exception as e:
                logger.error(e)
                raise

        logger.debug("Performing required validation.")
        errors = Validator.validate_required_checks(
            dataframe=dataframe,
            model_id=model_name,
            environment=environment,
            schema=schema,
            model_version=model_version,
            batch_id=batch_id,
        )
        if errors:
            for e in errors:
                logger.error(e)
            raise ValidationFailure(errors)

        if validate:
            logger.debug("Performing parameters validation.")
            errors = Validator.validate_params(
                dataframe=dataframe,
                model_id=model_name,
                model_type=model_type,
                environment=environment,
                schema=schema,
                metric_families=metrics_validation,
                model_version=model_version,
                batch_id=batch_id,
            )
            if errors:
                for e in errors:
                    logger.error(e)
                raise ValidationFailure(errors)

        logger.debug("Removing unnecessary columns.")
        dataframe = remove_extraneous_columns(df=dataframe, schema=schema)

        # always validate pd.Category is not present, if yes, convert to string
        has_cat_col = any(
            [ptypes.is_categorical_dtype(x) for x in dataframe.dtypes]
        )
        if has_cat_col:
            cat_cols = [
                col_name
                for col_name, col_cat in dataframe.dtypes.items()
                if col_cat.name == "category"
            ]
            cat_str_map = dict(zip(cat_cols, ["str"] * len(cat_cols)))
            dataframe = dataframe.astype(cat_str_map)

        if surrogate_explainability:
            require(_MIMIC_EXTRA, _MIMIC_DEPS)
            from arize.models.surrogate_explainer.mimic import Mimic

            logger.debug("Running surrogate_explainability.")
            if schema.shap_values_column_names:
                logger.info(
                    "surrogate_explainability=True has no effect "
                    "because shap_values_column_names is already specified in schema."
                )
            elif schema.feature_column_names is None or (
                hasattr(schema.feature_column_names, "__len__")
                and len(schema.feature_column_names) == 0
            ):
                logger.info(
                    "surrogate_explainability=True has no effect "
                    "because feature_column_names is empty or not specified in schema."
                )
            else:
                dataframe, schema = Mimic.augment(
                    df=dataframe, schema=schema, model_type=model_type
                )

        # Convert to Arrow table
        try:
            logger.debug("Converting data to Arrow format")
            # pyarrow will err if a mixed type column exist in the dataset even if
            # the column is not specified in schema. Caveat: There may be other
            # error conditions that we're currently not aware of.
            pa_table = pa.Table.from_pandas(dataframe)
        except pa.ArrowInvalid as e:
            logger.error(f"{INVALID_ARROW_CONVERSION_MSG}: {str(e)}")
            raise pa.ArrowInvalid(
                f"Error converting to Arrow format: {str(e)}"
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error creating Arrow table: {str(e)}")
            raise

        if validate:
            logger.debug("Performing types validation.")
            errors = Validator.validate_types(
                model_type=model_type,
                schema=schema,
                pyarrow_schema=pa_table.schema,
            )
            if errors:
                for e in errors:
                    logger.error(e)
                raise ValidationFailure(errors)
        if validate:
            logger.debug("Performing values validation.")
            errors = Validator.validate_values(
                dataframe=dataframe,
                environment=environment,
                schema=schema,
                model_type=model_type,
            )
            if errors:
                for e in errors:
                    logger.error(e)
                raise ValidationFailure(errors)

        if isinstance(schema, Schema) and not schema.has_prediction_columns():
            logger.warning(
                "Logging actuals without any predictions may result in "
                "unexpected behavior if corresponding predictions have not been logged prior. "
                "Please see the docs at https://docs.arize.com/arize/sending-data/sending-data-faq"
                "#what-happens-after-i-send-in-actual-data"
            )

        if environment == Environments.CORPUS:
            proto_schema = _get_pb_schema_corpus(
                schema=schema,
                model_id=model_name,
            )
        else:
            proto_schema = _get_pb_schema(
                schema=schema,
                model_id=model_name,
                model_version=model_version,
                model_type=model_type,
                environment=environment,
                batch_id=batch_id,
            )

        # Create headers copy for the spans client
        # Safe to mutate, returns a deep copy
        headers = self._sdk_config.headers
        # Send the number of rows in the dataframe as a header
        # This helps the Arize server to return appropriate feedback, specially for async logging
        headers.update(
            {
                "arize-space-id": space_id,
                "arize-interface": "batch",
                "number-of-rows": str(len(dataframe)),
            }
        )
        return post_arrow_table(
            files_url=self._sdk_config.files_url,
            pa_table=pa_table,
            proto_schema=proto_schema,
            headers=headers,
            timeout=timeout,
            verify=self._sdk_config.request_verify,
            tmp_dir=tmp_dir,
        )

    def export_to_df(
        self,
        space_id: str,
        model_name: str,
        environment: Environments,
        start_time: datetime,
        end_time: datetime,
        include_actuals: bool = False,
        model_version: str = "",
        batch_id: str = "",
        where: str = "",
        columns: List | None = None,
        similarity_search_params: SimilaritySearchParams | None = None,
        stream_chunk_size: int | None = None,
    ) -> pd.DataFrame:
        require(_BATCH_EXTRA, _BATCH_DEPS)
        from arize._exporter.client import ArizeExportClient
        from arize._flight.client import ArizeFlightClient

        with ArizeFlightClient(
            api_key=self._sdk_config.api_key,
            host=self._sdk_config.flight_server_host,
            port=self._sdk_config.flight_server_port,
            scheme=self._sdk_config.flight_scheme,
            request_verify=self._sdk_config.request_verify,
        ) as flight_client:
            exporter = ArizeExportClient(
                flight_client=flight_client,
            )
            return exporter.export_to_df(
                space_id=space_id,
                model_id=model_name,
                environment=environment,
                start_time=start_time,
                end_time=end_time,
                where=where,
                columns=columns,
                similarity_search_params=similarity_search_params,
                stream_chunk_size=stream_chunk_size,
                include_actuals=include_actuals,
                model_version=model_version,
                batch_id=batch_id,
            )

    def export_to_parquet(
        self,
        space_id: str,
        model_name: str,
        environment: Environments,
        start_time: datetime,
        end_time: datetime,
        include_actuals: bool = False,
        model_version: str = "",
        batch_id: str = "",
        where: str = "",
        columns: List | None = None,
        similarity_search_params: SimilaritySearchParams | None = None,
        stream_chunk_size: int | None = None,
    ) -> pd.DataFrame:
        require(_BATCH_EXTRA, _BATCH_DEPS)
        from arize._exporter.client import ArizeExportClient
        from arize._flight.client import ArizeFlightClient

        with ArizeFlightClient(
            api_key=self._sdk_config.api_key,
            host=self._sdk_config.flight_server_host,
            port=self._sdk_config.flight_server_port,
            scheme=self._sdk_config.flight_scheme,
            request_verify=self._sdk_config.request_verify,
        ) as flight_client:
            exporter = ArizeExportClient(
                flight_client=flight_client,
            )
            return exporter.export_to_parquet(
                space_id=space_id,
                model_id=model_name,
                environment=environment,
                start_time=start_time,
                end_time=end_time,
                where=where,
                columns=columns,
                similarity_search_params=similarity_search_params,
                stream_chunk_size=stream_chunk_size,
                include_actuals=include_actuals,
                model_version=model_version,
                batch_id=batch_id,
            )

    def _ensure_session(self) -> FuturesSession:
        from requests_futures.sessions import FuturesSession

        session = object.__getattribute__(self, "_session")
        if session is not None:
            return session

        # disable TLS verification for local dev on localhost, or if user opts out
        new_session = FuturesSession(
            executor=BoundedExecutor(
                self._sdk_config.stream_max_queue_bound,
                self._sdk_config.stream_max_workers,
            )
        )
        object.__setattr__(self, "_session", new_session)
        return new_session

    def _post(
        self,
        record: pb2.Record,
        headers: Dict[str, str],
        timeout: float | None,
        indexes: Tuple,
    ):
        from google.protobuf.json_format import MessageToDict

        session = self._ensure_session()
        resp = session.post(
            self._sdk_config.records_url,
            headers=headers,
            timeout=timeout,
            json=MessageToDict(
                message=record,
                preserving_proto_field_name=True,
            ),
            verify=self._sdk_config.request_verify,
        )
        if indexes is not None and len(indexes) == 2:
            resp.starting_index = indexes[0]
            resp.ending_index = indexes[1]
        return resp


def _validate_mapping_key(key_name: str, name: str):
    if not isinstance(key_name, str):
        raise ValueError(
            f"{name} dictionary key {key_name} must be named with string, type used: {type(key_name)}"
        )
    if key_name.endswith("_shap"):
        raise ValueError(
            f"{name} dictionary key {key_name} must not be named with a `_shap` suffix"
        )
    return


def _is_timestamp_in_range(now: int, ts: int):
    max_time = now + (MAX_FUTURE_YEARS_FROM_CURRENT_TIME * 365 * 24 * 60 * 60)
    min_time = now - (MAX_PAST_YEARS_FROM_CURRENT_TIME * 365 * 24 * 60 * 60)
    return min_time <= ts <= max_time


def _get_pb_schema(
    schema: Schema,
    model_id: str,
    model_version: str | None,
    model_type: ModelTypes,
    environment: Environments,
    batch_id: str,
):
    s = pb2.Schema()
    s.constants.model_id = model_id

    if model_version is not None:
        s.constants.model_version = model_version

    if environment == Environments.PRODUCTION:
        s.constants.environment = pb2.Schema.Environment.PRODUCTION
    elif environment == Environments.VALIDATION:
        s.constants.environment = pb2.Schema.Environment.VALIDATION
    elif environment == Environments.TRAINING:
        s.constants.environment = pb2.Schema.Environment.TRAINING
    else:
        raise ValueError(f"unexpected environment: {environment}")

    # Map user-friendly external model types -> internal model types when sending to Arize
    if model_type in NUMERIC_MODEL_TYPES:
        s.constants.model_type = pb2.Schema.ModelType.NUMERIC
    elif model_type in CATEGORICAL_MODEL_TYPES:
        s.constants.model_type = pb2.Schema.ModelType.SCORE_CATEGORICAL
    elif model_type == ModelTypes.RANKING:
        s.constants.model_type = pb2.Schema.ModelType.RANKING
    elif model_type == ModelTypes.OBJECT_DETECTION:
        s.constants.model_type = pb2.Schema.ModelType.OBJECT_DETECTION
    elif model_type == ModelTypes.GENERATIVE_LLM:
        s.constants.model_type = pb2.Schema.ModelType.GENERATIVE_LLM
    elif model_type == ModelTypes.MULTI_CLASS:
        s.constants.model_type = pb2.Schema.ModelType.MULTI_CLASS

    if batch_id is not None:
        s.constants.batch_id = batch_id

    if schema.prediction_id_column_name is not None:
        s.arrow_schema.prediction_id_column_name = (
            schema.prediction_id_column_name
        )

    if schema.timestamp_column_name is not None:
        s.arrow_schema.timestamp_column_name = schema.timestamp_column_name

    if schema.prediction_label_column_name is not None:
        s.arrow_schema.prediction_label_column_name = (
            schema.prediction_label_column_name
        )

    if model_type == ModelTypes.OBJECT_DETECTION:
        if schema.object_detection_prediction_column_names is not None:
            s.arrow_schema.prediction_object_detection_label_column_names.bboxes_coordinates_column_name = (
                schema.object_detection_prediction_column_names.bounding_boxes_coordinates_column_name  # noqa: E501
            )
            s.arrow_schema.prediction_object_detection_label_column_names.bboxes_categories_column_name = (
                schema.object_detection_prediction_column_names.categories_column_name  # noqa: E501
            )
            if (
                schema.object_detection_prediction_column_names.scores_column_name
                is not None
            ):
                s.arrow_schema.prediction_object_detection_label_column_names.bboxes_scores_column_name = (
                    schema.object_detection_prediction_column_names.scores_column_name  # noqa: E501
                )

        if schema.semantic_segmentation_prediction_column_names is not None:
            s.arrow_schema.prediction_semantic_segmentation_label_column_names.polygons_coordinates_column_name = (  # noqa: E501
                schema.semantic_segmentation_prediction_column_names.polygon_coordinates_column_name
            )
            s.arrow_schema.prediction_semantic_segmentation_label_column_names.polygons_categories_column_name = (  # noqa: E501
                schema.semantic_segmentation_prediction_column_names.categories_column_name
            )

        if schema.instance_segmentation_prediction_column_names is not None:
            s.arrow_schema.prediction_instance_segmentation_label_column_names.polygons_coordinates_column_name = (  # noqa: E501
                schema.instance_segmentation_prediction_column_names.polygon_coordinates_column_name
            )
            s.arrow_schema.prediction_instance_segmentation_label_column_names.polygons_categories_column_name = (  # noqa: E501
                schema.instance_segmentation_prediction_column_names.categories_column_name
            )
            if (
                schema.instance_segmentation_prediction_column_names.scores_column_name
                is not None
            ):
                s.arrow_schema.prediction_instance_segmentation_label_column_names.polygons_scores_column_name = (  # noqa: E501
                    schema.instance_segmentation_prediction_column_names.scores_column_name
                )
            if (
                schema.instance_segmentation_prediction_column_names.bounding_boxes_coordinates_column_name
                is not None
            ):
                s.arrow_schema.prediction_instance_segmentation_label_column_names.bboxes_coordinates_column_name = (  # noqa: E501
                    schema.instance_segmentation_prediction_column_names.bounding_boxes_coordinates_column_name
                )

    if schema.prediction_score_column_name is not None:
        if model_type in NUMERIC_MODEL_TYPES:
            # allow numeric prediction to be sent in as either prediction_label (legacy) or
            # prediction_score.
            s.arrow_schema.prediction_label_column_name = (
                schema.prediction_score_column_name
            )
        else:
            s.arrow_schema.prediction_score_column_name = (
                schema.prediction_score_column_name
            )

    if schema.feature_column_names is not None:
        s.arrow_schema.feature_column_names.extend(schema.feature_column_names)

    if schema.embedding_feature_column_names is not None:
        for (
            emb_name,
            emb_col_names,
        ) in schema.embedding_feature_column_names.items():
            # emb_name is how it will show in the UI
            s.arrow_schema.embedding_feature_column_names_map[
                emb_name
            ].vector_column_name = emb_col_names.vector_column_name
            if emb_col_names.data_column_name:
                s.arrow_schema.embedding_feature_column_names_map[
                    emb_name
                ].data_column_name = emb_col_names.data_column_name
            if emb_col_names.link_to_data_column_name:
                s.arrow_schema.embedding_feature_column_names_map[
                    emb_name
                ].link_to_data_column_name = (
                    emb_col_names.link_to_data_column_name
                )

    if schema.prompt_column_names is not None:
        if isinstance(schema.prompt_column_names, str):
            s.arrow_schema.embedding_feature_column_names_map[
                "prompt"
            ].data_column_name = schema.prompt_column_names
        elif isinstance(schema.prompt_column_names, EmbeddingColumnNames):
            col_names = schema.prompt_column_names
            s.arrow_schema.embedding_feature_column_names_map[
                "prompt"
            ].vector_column_name = col_names.vector_column_name
            if col_names.data_column_name:
                s.arrow_schema.embedding_feature_column_names_map[
                    "prompt"
                ].data_column_name = col_names.data_column_name
    if schema.response_column_names is not None:
        if isinstance(schema.response_column_names, str):
            s.arrow_schema.embedding_feature_column_names_map[
                "response"
            ].data_column_name = schema.response_column_names
        elif isinstance(schema.response_column_names, EmbeddingColumnNames):
            col_names = schema.response_column_names
            s.arrow_schema.embedding_feature_column_names_map[
                "response"
            ].vector_column_name = col_names.vector_column_name
            if col_names.data_column_name:
                s.arrow_schema.embedding_feature_column_names_map[
                    "response"
                ].data_column_name = col_names.data_column_name

    if schema.tag_column_names is not None:
        s.arrow_schema.tag_column_names.extend(schema.tag_column_names)

    if (
        model_type == ModelTypes.RANKING
        and schema.relevance_labels_column_name is not None
    ):
        s.arrow_schema.actual_label_column_name = (
            schema.relevance_labels_column_name
        )
    elif (
        model_type == ModelTypes.RANKING
        and schema.attributions_column_name is not None
    ):
        s.arrow_schema.actual_label_column_name = (
            schema.attributions_column_name
        )
    elif schema.actual_label_column_name is not None:
        s.arrow_schema.actual_label_column_name = (
            schema.actual_label_column_name
        )

    if (
        model_type == ModelTypes.RANKING
        and schema.relevance_score_column_name is not None
    ):
        s.arrow_schema.actual_score_column_name = (
            schema.relevance_score_column_name
        )
    elif schema.actual_score_column_name is not None:
        if model_type in NUMERIC_MODEL_TYPES:
            # allow numeric prediction to be sent in as either prediction_label (legacy) or
            # prediction_score.
            s.arrow_schema.actual_label_column_name = (
                schema.actual_score_column_name
            )
        else:
            s.arrow_schema.actual_score_column_name = (
                schema.actual_score_column_name
            )

    if schema.shap_values_column_names is not None:
        s.arrow_schema.shap_values_column_names.update(
            schema.shap_values_column_names
        )

    if schema.prediction_group_id_column_name is not None:
        s.arrow_schema.prediction_group_id_column_name = (
            schema.prediction_group_id_column_name
        )

    if schema.rank_column_name is not None:
        s.arrow_schema.rank_column_name = schema.rank_column_name

    if model_type == ModelTypes.OBJECT_DETECTION:
        if schema.object_detection_actual_column_names is not None:
            s.arrow_schema.actual_object_detection_label_column_names.bboxes_coordinates_column_name = (  # noqa: E501
                schema.object_detection_actual_column_names.bounding_boxes_coordinates_column_name
            )
            s.arrow_schema.actual_object_detection_label_column_names.bboxes_categories_column_name = (  # noqa: E501
                schema.object_detection_actual_column_names.categories_column_name
            )
            if (
                schema.object_detection_actual_column_names.scores_column_name
                is not None
            ):
                s.arrow_schema.actual_object_detection_label_column_names.bboxes_scores_column_name = (  # noqa: E501
                    schema.object_detection_actual_column_names.scores_column_name
                )

        if schema.semantic_segmentation_actual_column_names is not None:
            s.arrow_schema.actual_semantic_segmentation_label_column_names.polygons_coordinates_column_name = (  # noqa: E501
                schema.semantic_segmentation_actual_column_names.polygon_coordinates_column_name
            )
            s.arrow_schema.actual_semantic_segmentation_label_column_names.polygons_categories_column_name = (  # noqa: E501
                schema.semantic_segmentation_actual_column_names.categories_column_name
            )

        if schema.instance_segmentation_actual_column_names is not None:
            s.arrow_schema.actual_instance_segmentation_label_column_names.polygons_coordinates_column_name = (  # noqa: E501
                schema.instance_segmentation_actual_column_names.polygon_coordinates_column_name
            )
            s.arrow_schema.actual_instance_segmentation_label_column_names.polygons_categories_column_name = (  # noqa: E501
                schema.instance_segmentation_actual_column_names.categories_column_name
            )
            if (
                schema.instance_segmentation_actual_column_names.bounding_boxes_coordinates_column_name
                is not None
            ):
                s.arrow_schema.actual_instance_segmentation_label_column_names.bboxes_coordinates_column_name = (  # noqa: E501
                    schema.instance_segmentation_actual_column_names.bounding_boxes_coordinates_column_name
                )

    if model_type == ModelTypes.GENERATIVE_LLM:
        if schema.prompt_template_column_names is not None:
            s.arrow_schema.prompt_template_column_names.template_column_name = (
                schema.prompt_template_column_names.template_column_name
            )
            s.arrow_schema.prompt_template_column_names.template_version_column_name = (  # noqa: E501
                schema.prompt_template_column_names.template_version_column_name
            )
        if schema.llm_config_column_names is not None:
            s.arrow_schema.llm_config_column_names.model_column_name = (
                schema.llm_config_column_names.model_column_name
            )
            s.arrow_schema.llm_config_column_names.params_map_column_name = (
                schema.llm_config_column_names.params_column_name
            )
        if schema.retrieved_document_ids_column_name is not None:
            s.arrow_schema.retrieved_document_ids_column_name = (
                schema.retrieved_document_ids_column_name
            )
    if model_type == ModelTypes.MULTI_CLASS:
        if schema.prediction_score_column_name is not None:
            s.arrow_schema.prediction_score_column_name = (
                schema.prediction_score_column_name
            )
        if schema.multi_class_threshold_scores_column_name is not None:
            s.arrow_schema.multi_class_threshold_scores_column_name = (
                schema.multi_class_threshold_scores_column_name
            )
        if schema.actual_score_column_name is not None:
            s.arrow_schema.actual_score_column_name = (
                schema.actual_score_column_name
            )
    return s


def _get_pb_schema_corpus(
    schema: CorpusSchema,
    model_id: str,
) -> pb2.Schema:
    s = pb2.Schema()
    s.constants.model_id = model_id
    s.constants.environment = pb2.Schema.Environment.CORPUS
    s.constants.model_type = pb2.Schema.ModelType.GENERATIVE_LLM
    if schema.document_id_column_name is not None:
        s.arrow_schema.document_column_names.id_column_name = (
            schema.document_id_column_name
        )
    if schema.document_version_column_name is not None:
        s.arrow_schema.document_column_names.version_column_name = (
            schema.document_version_column_name
        )
    if schema.document_text_embedding_column_names is not None:
        s.arrow_schema.document_column_names.text_column_name.vector_column_name = schema.document_text_embedding_column_names.vector_column_name  # noqa: E501
        s.arrow_schema.document_column_names.text_column_name.data_column_name = schema.document_text_embedding_column_names.data_column_name  # noqa: E501
        if (
            schema.document_text_embedding_column_names.link_to_data_column_name
            is not None
        ):
            s.arrow_schema.document_column_names.text_column_name.link_to_data_column_name = schema.document_text_embedding_column_names.link_to_data_column_name  # noqa: E501
    return s
