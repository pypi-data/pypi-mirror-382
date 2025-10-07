from collections.abc import Mapping

from arize._generated.api_client import models


def make_to_df(field_name: str):
    def to_df(
        self,
        by_alias: bool = False,
        exclude_none: str | bool = False,
        json_normalize: bool = False,
        convert_dtypes: bool = True,
    ):
        """
        Convert a list of objects to a pandas DataFrame.

        Behavior:
          - If an item is a Pydantic v2 model, use `.model_dump(by_alias=...)`.
          - If an item is a mapping (dict-like), use it as-is.
          - Otherwise, raise a ValueError (unsupported row type).

        Parameters:
          by_alias: Use field aliases when dumping Pydantic models.
          exclude_none:
            - False: keep Nones as-is
            - "all": drop columns where *all* values are None/NaN
            - "any": drop columns where *any* value is None/NaN
            - True: alias for "all"
          json_normalize: If True, flatten nested dicts via `pandas.json_normalize`.
          convert_dtypes: If True, call `DataFrame.convert_dtypes()` at the end.

        Returns:
          pandas.DataFrame
        """
        import pandas as pd

        items = getattr(self, field_name, []) or []

        rows = []
        for it in items:
            if hasattr(it, "model_dump"):  # Pydantic v2 object
                rows.append(it.model_dump(by_alias=by_alias))

            elif isinstance(it, Mapping):  # Plain mapping
                rows.append(it)
            else:
                raise ValueError(
                    f"Cannot convert item of type {type(it)} to DataFrame row"
                )

        df = (
            pd.json_normalize(rows, sep=".")
            if json_normalize
            else pd.DataFrame(rows)
        )

        # Drop None/NaN columns if requested
        if exclude_none in ("any", "all", True):
            drop_how = "all" if exclude_none is True else exclude_none
            df.dropna(axis=1, how=drop_how, inplace=True)

        if convert_dtypes:
            df = df.convert_dtypes()
        return df

    return to_df


models.DatasetsList200Response.to_df = make_to_df("datasets")  # type: ignore[attr-defined]
models.DatasetsListExamples200Response.to_df = make_to_df("examples")  # type: ignore[attr-defined]
