from __future__ import annotations

import logging
from typing import Any, Dict, List

import pandas as pd
import pyarrow as pa

from arize._flight.client import ArizeFlightClient
from arize.config import SDKConfiguration
from arize.exceptions.base import INVALID_ARROW_CONVERSION_MSG

logger = logging.getLogger(__name__)

REST_LIMIT_DATASET_EXAMPLES = 3


class DatasetsClient:
    def __init__(self, sdk_config: SDKConfiguration):
        self._sdk_config = sdk_config

        # Import at runtime so it’s still lazy and extras-gated by the parent
        from arize._generated import api_client as gen

        # Use the shared generated client from the config
        self._api = gen.DatasetsApi(self._sdk_config.get_generated_client())

        # Forward methods to preserve exact runtime signatures/docs
        self.list = self._api.datasets_list
        self.get = self._api.datasets_get
        self.delete = self._api.datasets_delete
        self.list_examples = self._api.datasets_list_examples

        # Custom methods
        self.create = self._create_dataset

    def _create_dataset(
        self,
        name: str,
        space_id: str,
        examples: List[Dict[str, Any]] | pd.DataFrame,
        force_http: bool = False,
    ):
        if not isinstance(examples, (list, pd.DataFrame)):
            raise TypeError(
                "Examples must be a list of dicts or a pandas DataFrame"
            )
        if len(examples) <= REST_LIMIT_DATASET_EXAMPLES or force_http:
            from arize._generated import api_client as gen

            data = (
                examples.to_dict(orient="records")
                if isinstance(examples, pd.DataFrame)
                else examples
            )

            body = gen.DatasetsCreateRequest(
                name=name,
                spaceId=space_id,
                examples=data,
            )
            return self._api.datasets_create(datasets_create_request=body)

        # If we have too many examples, try to convert to a dataframe
        # and log via gRPC + flight
        logger.info(
            f"Uploading {len(examples)} examples via REST may be slow. "
            "Trying to convert to DataFrame for more efficient upload via "
            "gRPC + Flight."
        )
        data = (
            pd.DataFrame(examples) if isinstance(examples, list) else examples
        )
        return self._create_dataset_via_flight(
            name=name,
            space_id=space_id,
            examples=data,
        )

    def _create_dataset_via_flight(
        self,
        name: str,
        space_id: str,
        examples: pd.DataFrame,
    ):
        # Convert datetime columns to int64 (ms since epoch)
        # TODO(Kiko): Missing validation block
        # data = _convert_datetime_columns_to_int(data)
        # df = self._set_default_columns_for_dataset(data)
        # if convert_dict_to_json:
        #     df = _convert_default_columns_to_json_str(df)
        # df = _convert_boolean_columns_to_str(df)
        # validation_errors = Validator.validate(df)
        # validation_errors.extend(
        #     Validator.validate_max_chunk_size(max_chunk_size)
        # )
        # if validation_errors:
        #     raise RuntimeError(
        #         [e.error_message() for e in validation_errors]
        #     )

        # Convert to Arrow table
        try:
            logger.debug("Converting data to Arrow format")
            pa_table = pa.Table.from_pandas(examples)
        except pa.ArrowInvalid as e:
            logger.error(f"{INVALID_ARROW_CONVERSION_MSG}: {str(e)}")
            raise pa.ArrowInvalid(
                f"Error converting to Arrow format: {str(e)}"
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error creating Arrow table: {str(e)}")
            raise

        response = None
        with ArizeFlightClient(
            api_key=self._sdk_config.api_key,
            host=self._sdk_config.flight_server_host,
            port=self._sdk_config.flight_server_port,
            scheme=self._sdk_config.flight_scheme,
            request_verify=self._sdk_config.request_verify,
        ) as flight_client:
            try:
                response = flight_client.create_dataset(
                    space_id=space_id,
                    dataset_name=name,
                    pa_table=pa_table,
                )
            except Exception as e:
                msg = f"Error during update request: {str(e)}"
                logger.error(msg)
                raise RuntimeError(msg) from e
        if response is None:
            # This should not happen with proper Flight client implementation,
            # but we handle it defensively
            msg = "No response received from flight server during update"
            logger.error(msg)
            raise RuntimeError(msg)
        # The response from flightserver is the dataset ID. To return the dataset
        # object we make a GET query
        dataset = self.get(dataset_id=response)
        return dataset
