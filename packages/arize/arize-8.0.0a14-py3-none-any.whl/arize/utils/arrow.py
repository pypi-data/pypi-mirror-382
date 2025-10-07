# type: ignore[pb2]
from __future__ import annotations

import base64
import logging
import os
import tempfile
from typing import TYPE_CHECKING, Any, Dict

import pyarrow as pa

from arize.logging import get_arize_project_url, log_a_list

if TYPE_CHECKING:
    import requests

    from arize._generated.protocol.rec import public_pb2 as pb2

logger = logging.getLogger(__name__)


def post_arrow_table(
    files_url: str,
    pa_table: pa.Table,
    proto_schema: pb2.Schema,
    headers: Dict[str, str],
    timeout: float | None,
    verify: bool,
    tmp_dir: str = "",
) -> requests.Response:
    # We import here to avoid depending onn requests for all arrow utils
    import requests

    logger.debug("Preparing to log Arrow table via file upload")
    logger.debug(
        "Preparing to log Arrow table via file upload",
        extra={"rows": pa_table.num_rows, "cols": pa_table.num_columns},
    )

    logger.debug("Serializing schema")
    base64_schema = base64.b64encode(proto_schema.SerializeToString())
    pa_schema = _append_to_pyarrow_metadata(
        pa_table.schema, {"arize-schema": base64_schema}
    )

    # --- decide output file path ---
    # cases:
    # 1) tmp_dir == ""        -> we own a TemporaryDirectory, we write to a file
    #                            in it, clean the entire dir
    # 2) tmp_dir is a dir     -> user owns the directory, we create a temp file
    #                            inside it (and remove only that file)
    # 3) tmp_dir is a file    -> user owns the file, we write exactly there (no cleanup)

    tdir = None  # Assume caller owns the directory
    cleanup_file = False
    if not tmp_dir:
        # we own the directory. Best effort cleanup on Windows:
        # https://www.scivision.dev/python-tempfile-permission-error-windows/
        tdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        outfile = _mktemp_in(tdir.name)
    elif os.path.isdir(tmp_dir):
        outfile = _mktemp_in(tmp_dir)
        cleanup_file = True  # we own the file
    else:
        # explicit file path
        outfile = tmp_dir

    try:
        # Write arrow file
        logger.debug(f"Writing table to temporary file: {outfile}")
        _write_arrow_file(outfile, pa_table, pa_schema)

        # Send to Arize
        logger.debug(
            "Uploading file to Arize",
            extra={"path": outfile, "size_bytes": _filesize(outfile)},
        )
        # Post file
        with open(outfile, "rb") as f:
            resp = requests.post(
                files_url,
                timeout=timeout,
                data=f,
                headers=headers,
                verify=verify,
            )
            _maybe_log_project_url(resp)
            return resp
    finally:
        if tdir is not None:
            try:
                # triggers TemporaryDirectory cleanup (best-effort on Windows)
                tdir.cleanup()  # cleaning the entire dir, no need to clean the file
            except Exception as e:
                logger.warning(
                    f"Failed to remove temporary directory {tdir.name}: {str(e)}"
                )
        elif cleanup_file:
            try:
                os.remove(outfile)
            except Exception as e:
                logger.warning(
                    f"Failed to remove temporary file {outfile}: {str(e)}"
                )


def _append_to_pyarrow_metadata(
    pa_schema: pa.Schema, new_metadata: Dict[str, Any]
):
    # Ensure metadata is handled correctly, even if initially None.
    metadata = pa_schema.metadata
    if metadata is None:
        # Initialize an empty dict if schema metadata was None
        metadata = {}

    conflicting_keys = metadata.keys() & new_metadata.keys()
    if conflicting_keys:
        raise KeyError(
            "Cannot append metadata to pyarrow schema. "
            f"There are conflicting keys: {log_a_list(conflicting_keys, join_word='and')}"
        )

    updated_metadata = metadata.copy()
    updated_metadata.update(new_metadata)
    return pa_schema.with_metadata(updated_metadata)


def _write_arrow_file(
    path: str, pa_table: pa.Table, pa_schema: pa.Schema
) -> None:
    with pa.OSFile(path, mode="wb") as sink, pa.ipc.RecordBatchStreamWriter(
        sink, pa_schema
    ) as writer:
        writer.write_table(pa_table, max_chunksize=16384)


def _maybe_log_project_url(response: requests.Response) -> None:
    try:
        url = get_arize_project_url(response)
        if url:
            logger.info("✅ Success! Check out your data at %s", url)
    except Exception as e:
        logger.warning("Failed to get project URL: %s", e)


def _mktemp_in(directory: str) -> str:
    """
    Create a unique temp file path inside `directory` without leaving
    an open file descriptor around (Windows-safe). The file exists on
    disk and is closed; caller can open/write it later.
    """
    with tempfile.NamedTemporaryFile(
        dir=directory,
        prefix="arize-",
        suffix=".arrow",
        delete=False,  # important on Windows: don't keep the file open
    ) as f:
        return f.name  # file is closed when we exit the context


def _filesize(path: str) -> int:
    try:
        return os.path.getsize(path)
    except Exception:
        return -1
