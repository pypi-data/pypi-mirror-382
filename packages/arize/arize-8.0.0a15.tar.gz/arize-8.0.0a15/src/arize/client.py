from __future__ import annotations

from typing import TYPE_CHECKING

from arize._lazy import LazySubclientsMixin
from arize.config import SDKConfiguration

if TYPE_CHECKING:
    from arize.datasets.client import DatasetsClient
    from arize.experiments.client import ExperimentsClient
    from arize.models.client import MLModelsClient
    from arize.spans.client import SpansClient


# TODO(Kiko): Add flight max_chunksize opt to write_table. In config?
# TODO(Kiko): experimental/datasets must be adapted into the datasets subclient
# TODO(Kiko): experimental/prompt hub is missing
# TODO(Kiko): exporter/utils/schema_parser is missing
# TODO(Kiko): Go through main APIs and add CtxAdapter where missing
# TODO(Kiko): Search and handle other TODOs
# TODO(Kiko): Go over **every file** and do not import anything at runtime, use `if TYPE_CHECKING`
# with `from __future__ import annotations` (must include for Python < 3.11)
# TODO(Kiko): Go over docstrings
class ArizeClient(LazySubclientsMixin):
    """
    Root client for the Arize SDK. All parameters are optional. If not provided, they will be read
    from environment variables. If those are absent, built-in defaults will be used with the only
    exception of `api_key`, which is required to be provided either via argument or environment
    variable (ARIZE_API_KEY).

    Parameters (all optional):
        api_key: If not provided, read from environment (ARIZE_API_KEY). If absent, raises.
        api_host: If not provided, read from environment (ARIZE_API_HOST) or default.
        api_scheme: If not provided, read from environment (ARIZE_API_INSECURE -> http/https) or default.
        flight_server_host: If not provided, read from environment (ARIZE_FLIGHT_HOST) or default.
        flight_server_port: If not provided, read from environment (ARIZE_FLIGHT_PORT) or default.
        flight_scheme: If not provided, read from environment (ARIZE_FLIGHT_TRANSPORT_SCHEME) or default.
        request_verify: If not provided, read from environment (ARIZE_REQUEST_VERIFY) or defaults to True.

    Resolution order for each field:
        1) Value passed here (if not None)
        2) Environment variable (handled by SDKConfiguration class)
        3) Built-in default constant (handled by SDKConfiguration class)
    """

    _SUBCLIENTS = {
        "datasets": (
            "arize.datasets.client",
            "DatasetsClient",
        ),
        "experiments": (
            "arize.experiments.client",
            "ExperimentsClient",
        ),
        "spans": (
            "arize.spans.client",
            "SpansClient",
        ),
        "models": (
            "arize.models.client",
            "MLModelsClient",
        ),
    }
    _EXTRAS = {
        # Gate only the generated-backed ones
        "datasets": (
            "datasets-experiments",
            ("pydantic",),
        ),
        "experiments": (
            "datasets-experiments",
            ("pydantic",),
        ),
        "spans": (
            "spans",
            (
                "google.protobuf",
                "numpy",
                "openinference.semconv",
                "opentelemetry",
                "pandas",
                "pyarrow",
                "requests",
                "tqdm",
            ),
        ),
        # Imports are gated in each method of the models client
        # This is to allow for very lean package install if people only
        # want to stream ML records
        "models": (None, ()),
    }

    def __init__(
        self,
        api_key: str | None = None,
        api_host: str | None = None,
        api_scheme: str | None = None,
        flight_server_host: str | None = None,
        flight_server_port: int | None = None,
        flight_scheme: str | None = None,
        request_verify: bool | None = None,
        stream_max_workers: int | None = None,
        stream_max_queue_bound: int | None = None,
    ):
        cfg_kwargs: dict = {}
        if api_key is not None:
            cfg_kwargs["api_key"] = api_key
        if api_host is not None:
            cfg_kwargs["api_host"] = api_host
        if api_scheme is not None:
            cfg_kwargs["api_scheme"] = api_scheme
        if flight_server_host is not None:
            cfg_kwargs["flight_server_host"] = flight_server_host
        if flight_server_port is not None:
            cfg_kwargs["flight_server_port"] = flight_server_port
        if flight_scheme is not None:
            cfg_kwargs["flight_scheme"] = flight_scheme
        if request_verify is not None:
            cfg_kwargs["request_verify"] = request_verify
        if stream_max_workers is not None:
            cfg_kwargs["stream_max_workers"] = stream_max_workers
        if stream_max_queue_bound is not None:
            cfg_kwargs["stream_max_queue_bound"] = stream_max_queue_bound

        # Only the explicitly provided fields are passed; the rest use
        # SDKConfiguration’s default factories / defaults.
        super().__init__(SDKConfiguration(**cfg_kwargs))

    # typed properties for IDE completion
    @property
    def datasets(self) -> DatasetsClient:
        return self.__getattr__("datasets")

    @property
    def experiments(self) -> ExperimentsClient:
        return self.__getattr__("experiments")

    @property
    def spans(self) -> SpansClient:
        return self.__getattr__("spans")

    @property
    def models(self) -> MLModelsClient:
        return self.__getattr__("models")

    def __repr__(self) -> str:
        lines = [f"{self.__class__.__name__}("]
        # Indent the SDKConfiguration repr
        cfg_repr = repr(self.sdk_config).splitlines()
        lines.append(f"  sdk_config={cfg_repr[0]}")
        lines.extend("  " + line for line in cfg_repr[1:])
        # Add subclient states
        lines.append("  subclients={")
        for name in self._SUBCLIENTS:
            state = "loaded" if name in self._lazy_cache else "lazy"
            lines.append(f"    {name!r}: {state},")
        lines.append("  }")
        lines.append(")")
        return "\n".join(lines)
