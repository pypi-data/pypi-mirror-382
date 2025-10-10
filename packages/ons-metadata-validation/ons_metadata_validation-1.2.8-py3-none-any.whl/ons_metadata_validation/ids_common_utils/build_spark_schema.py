"""Module to build Spark schema from metadata template. Handles nested columns validations here if necessary."""

import re
from typing import Any, Dict, List, Tuple

from pyspark.sql.types import StructType

from ons_metadata_validation.ids_common_utils.nested_columns import (
    evaluate_nested_columns,
)
from ons_metadata_validation.ids_common_utils.spark_datatype import (
    build_spark_schema_from_json,
)
from ons_metadata_validation.processing.data_structures import Fail
from ons_metadata_validation.reference.constants import MetaMapper, SheetMapper

SeriesSchemas = Dict[str, StructType]
ModifiedJSON = Dict[str, Any]
NestedColumnErrors = Dict[str, List[Fail]]


def get_schemas_for_series(
    json: dict, version_number: str
) -> Tuple[SeriesSchemas, ModifiedJSON, NestedColumnErrors]:
    """Get spark schemas for each data series in JSON.
    Args:
        json (dict): The converted metadata template
        version_number (str): The version number as parsed from the ConvertExcelMetadata.
    Returns:
        Tuple[SeriesSchemas, ModifiedJSON, NestedColumnErrors].
    """
    schemas, validated_json, errors = {}, {}, {}

    for series_name, series in json[SheetMapper.SERIES.value].items():
        try:
            col_json = series[SheetMapper.VARS.value]
        except KeyError as e:
            print(
                f"KeyError: {e} getting '{SheetMapper.VARS.value}' for '{series_name}'. Can't make schema, skipping."
            )
            continue

        # add the column names to the json entries
        for k, v in col_json.items():
            v.update({MetaMapper.VARS_variable_name.value: k})

        # condition for when there's a new metadata version template
        if float(re.sub("[A-Z]", "", version_number)) >= 3.0:
            col_json, val_errors = evaluate_nested_columns(col_json)
            validated_json[series_name] = col_json
            errors[series_name] = val_errors

        schemas[series_name] = build_spark_schema_from_json(col_json)

    return schemas, validated_json, errors
