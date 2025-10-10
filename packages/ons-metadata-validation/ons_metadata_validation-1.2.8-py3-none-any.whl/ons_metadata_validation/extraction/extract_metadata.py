"""This is for internal ONS use only, it makes some assumptions about the way the data is
stored that may not hold true for external suppliers and therefore we'd need to refactor
if we wanted to promote this for public use.
"""

import json
import os
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

import numpy as np
import pandas as pd
import pyspark.sql as spark
from openpyxl import load_workbook

import ons_metadata_validation.extraction.metadata_utils as mdu
import ons_metadata_validation.processing.utils as utils
from ons_metadata_validation.processing.data_structures import DataDetails
from ons_metadata_validation.reference.constants import (
    MetaMapper,
    SheetMapper,
    SupplyType,
)


def extract_structural_metadata(
    empty_md_filepath: str,
    data_filepaths: List[str],
    target_version: str,
    metadata_savepath: str,
    read_func: Callable[[str], spark.DataFrame],
    md5_func: Callable[[str], str],
    size_func: Callable[[str], Union[str, int]],
    use_folder_name: bool = True,
    bucket_prefix: str = "",
) -> None:
    """Main function to extract structural metadata.

    Args:
        empty_md_filepath (str): path to the empty metadata template.
        data_filepaths (List[str]): path(s) to the data to extract from.
        target_version (str): the target metadata template version.
        metadata_savepath (str): where to save the completed metadata.
        read_func (Callable[[str], spark.DataFrame]): read function that returns a spark dataframe.
        md5_func (Callable[[str], str]): md5 function that returns the md5 as a string
        size_func (Callable[[str], Union[str, int]]): the size function that returns the size as a string or int
        use_folder_name (bool, optional): Use the folder above the file for the table name. Defaults to True.
        bucket_prefix (str, optional): the bucket prefix to remove from any filepaths. Defaults to "".
    """
    wb = load_workbook(empty_md_filepath, data_only=True)
    template_map, _ = utils.get_template_map(target_version)
    utils.validate_metadata_structure(template_map, wb)
    data_details = [
        _inspect_data(f, read_func, md5_func, size_func) for f in data_filepaths
    ]
    structural_extracts = {
        SheetMapper.SERIES.value: fill_dataset_series_tab(
            data_details, use_folder_name
        ),
        SheetMapper.FILE.value: fill_dataset_file_tab(
            data_details, bucket_prefix, use_folder_name
        ),
        SheetMapper.VARS.value: fill_variables_tab(data_details, use_folder_name),
    }
    utils.write_dfs_to_wb(template_map, structural_extracts, wb)
    os.makedirs(os.path.dirname(metadata_savepath), exist_ok=True)
    wb.save(metadata_savepath)


def fill_dataset_series_tab(
    data_details: Sequence[DataDetails], use_folder_name: bool = True
) -> pd.DataFrame:
    """Fill the Dataset Series tab from the DataDetails.

    Args:
        data_details (Sequence[DataDetails]): the DataDetails to extract.
        use_folder_name (bool, optional): Use the folder above the file for the table name. Defaults to True.

    Returns:
        pd.DataFrame: The filled Dataset Series tab
    """
    dataset_series = pd.DataFrame(
        [{MetaMapper.SERIES_dataset_series_name.value: d.path} for d in data_details]
    )
    dataset_series[
        MetaMapper.SERIES_google_cloud_platform_bigquery_table_name.value
    ] = dataset_series[MetaMapper.SERIES_dataset_series_name.value].apply(
        lambda x: mdu.get_big_query_name(x, use_folder_name)
    )
    dataset_series[MetaMapper.SERIES_dataset_series_name.value] = dataset_series[
        MetaMapper.SERIES_google_cloud_platform_bigquery_table_name.value
    ].apply(mdu.get_dataset_series_name)

    # Trailing space to match enum in template
    dataset_series[MetaMapper.SERIES_supply_type.value] = SupplyType.FULL.value

    dataset_series = dataset_series.drop_duplicates(
        subset=[MetaMapper.SERIES_google_cloud_platform_bigquery_table_name.value]
    ).reset_index(drop=True)
    return dataset_series.convert_dtypes().fillna("")


def fill_dataset_file_tab(
    data_details: Sequence[DataDetails],
    bucket_prefix: str = "",
    use_folder_name: bool = True,
) -> pd.DataFrame:
    """Fill the Dataset File tab from the DataDetails.

    Args:
        data_details (Sequence[DataDetails]): the DataDetails to extract.
        bucket_prefix (str, optional): the bucket prefix to remove from any filepaths. Defaults to "".
        use_folder_name (bool, optional): Use the folder above the file for the table name. Defaults to True.

    Returns:
        pd.DataFrame: The filled Dataset File tab
    """
    dataset_file = pd.DataFrame(
        [
            {
                MetaMapper.FILE_file_path_and_name.value: d.path,
                MetaMapper.FILE_number_of_records.value: d.n_rows,
                MetaMapper.FILE_file_size.value: d.size,
                MetaMapper.FILE_hash_value_for_checksum.value: d.md5,
            }
            for d in data_details
        ]
    )
    if bucket_prefix:
        dataset_file[MetaMapper.FILE_file_path_and_name.value] = dataset_file[
            MetaMapper.FILE_file_path_and_name.value
        ].str.replace(bucket_prefix, "")

    dataset_file[MetaMapper.FILE_google_cloud_platform_bigquery_table_name.value] = (
        dataset_file[MetaMapper.FILE_file_path_and_name.value].apply(
            lambda x: mdu.get_big_query_name(x, use_folder_name)
        )
    )
    dataset_file[MetaMapper.FILE_file_format.value] = dataset_file[
        MetaMapper.FILE_file_path_and_name.value
    ].apply(mdu.get_file_format)
    dataset_file[MetaMapper.FILE_file_size.value] = (
        dataset_file[MetaMapper.FILE_file_size.value] / 1000
    )
    dataset_file[MetaMapper.FILE_file_size_unit.value] = "KB"
    dataset_file[MetaMapper.FILE_number_of_header_rows.value] = np.where(
        dataset_file[MetaMapper.FILE_file_format.value] == "CSV", 1, 0
    )
    dataset_file[MetaMapper.FILE_number_of_footer_rows.value] = 0
    dataset_file[MetaMapper.FILE_character_encoding.value] = "UTF-8"
    duplicated_tables = mdu.get_duplicates(
        dataset_file[
            MetaMapper.FILE_google_cloud_platform_bigquery_table_name.value
        ].to_list()
    )
    dataset_file[
        MetaMapper.FILE_is_this_file_one_of_a_sequence_to_be_appended_back_together.value
    ] = dataset_file[
        MetaMapper.FILE_google_cloud_platform_bigquery_table_name.value
    ].apply(lambda x: mdu.is_duplicated(x, duplicated_tables))
    dataset_file[MetaMapper.FILE_column_seperator.value] = np.where(
        dataset_file[MetaMapper.FILE_file_format.value] == "CSV", ",", ""
    )

    return dataset_file.convert_dtypes().fillna("")


def fill_variables_tab(
    data_details: Sequence[DataDetails], use_folder_name: bool = True
) -> pd.DataFrame:
    """Fill the Variables tab from the DataDetails.

    Args:
        data_details (Sequence[DataDetails]): the DataDetails to extract.
        use_folder_name (bool, optional): Use the folder above the file for the table name. Defaults to True.

    Returns:
        pd.DataFrame: The filled Variables tab
    """
    unpacked_variables = _unpack_nested_types(
        pd.concat([d.schema for d in data_details]).to_dict("records")
    )
    variables = pd.DataFrame(unpacked_variables).rename(
        columns={
            "path": MetaMapper.VARS_google_cloud_platform_bigquery_table_name.value,
            "name": MetaMapper.VARS_variable_name.value,
            "type": MetaMapper.VARS_variable_data_type.value,
            "nullable": MetaMapper.VARS_nullability.value,
            "keyType": MetaMapper.VARS_key_data_type.value,
            "valueType": MetaMapper.VARS_value_data_type.value,
        }
    )

    variables[MetaMapper.VARS_google_cloud_platform_bigquery_table_name.value] = (
        variables[
            MetaMapper.VARS_google_cloud_platform_bigquery_table_name.value
        ].apply(lambda x: mdu.get_big_query_name(x, use_folder_name))
    )
    variables = variables.drop_duplicates(
        subset=[
            MetaMapper.VARS_google_cloud_platform_bigquery_table_name.value,
            MetaMapper.VARS_variable_name.value,
        ]
    ).reset_index(drop=True)

    metadata_funcs = [
        (
            MetaMapper.VARS_nullability.value,
            MetaMapper.VARS_nullability.value,
            mdu.is_nullable,
        ),
        (
            MetaMapper.VARS_variable_length_precision.value,
            MetaMapper.VARS_variable_data_type.value,
            mdu.get_length_precision,
        ),
        (
            MetaMapper.VARS_variable_data_type.value,
            MetaMapper.VARS_variable_data_type.value,
            mdu.remove_decimal_precision,
        ),
        (
            MetaMapper.VARS_variable_format.value,
            MetaMapper.VARS_variable_data_type.value,
            mdu.get_date_format,
        ),
    ]
    for dst_col, src_col, func in metadata_funcs:
        variables[dst_col] = variables[src_col].apply(func)

    return variables.convert_dtypes().fillna("")


def _inspect_data(
    path: str,
    read_func: Callable[[str], spark.DataFrame],
    md5_func: Callable[[str], str],
    size_func: Callable[[str], Union[str, int]],
) -> DataDetails:
    """Get the DataDetails for the path.

    Args:
        path (str): the path to inspect
        read_func (Callable[[str], spark.DataFrame]): read function that returns a spark dataframe.
        md5_func (Callable[[str], str]): md5 function that returns the md5 as a string.
        size_func (Callable[[str], Union[str, int]]): the size function that returns the size as a string or int.

    Returns:
        DataDetails: returns these details for the path:
            path: str
            md5: str
            n_rows: int
            schema: pd.DataFrame
            size: int
    """
    data = read_func(path)
    n_rows = data.count()

    schema = pd.DataFrame(json.loads(data.schema.json())["fields"])
    schema["path"] = path

    if path.endswith(".parquet"):
        # avoid schema mismatch error due to change in ids_common_utils
        schema["type"] = schema["type"].replace({"integer": "integertype"})

    details = DataDetails(
        path,
        md5_func(path),
        n_rows,
        schema,
        int(size_func(path)),
    )
    print(details.path)
    return details


def _unpack_nested_types(
    fields: List[Dict[str, Any]], parent: Optional[Dict] = None
) -> List[Dict[str, str]]:
    def _unpack_struct(node: dict, field_type: dict, key: str) -> None:
        if (
            isinstance(field_type.get(key), dict)
            and field_type[key].get("type", "") == "struct"
        ):
            node["valueType"] = "struct"
            records.append(node)
            # have to add a struct record between the valueType struct and the
            # struct values
            value_node = {
                "path": node.get("path", ""),
                "name": node.get("name", "") + ".value",
                "nullable": node.get("nullable", True),
                "type": "struct",
                "keyType": "",
                "valueType": "",
            }
            records.append(value_node)
            records.extend(_unpack_nested_types(field_type[key]["fields"], value_node))
        else:
            records.append(node)

    records = []
    parent = parent or {}

    for field in fields:
        field_name = f"{parent['name']}.{field['name']}" if parent else field["name"]
        field_type = field.get("type")

        node = {
            "path": field.get("path", parent.get("path")),
            "name": field_name,
            "nullable": field.get("nullable", True),
            "type": "",
            "keyType": "",
            "valueType": "",
        }

        if isinstance(field_type, dict):
            if field_type.get("type", "") == "struct":
                node["type"] = "struct"
                records.append(node)
                records.extend(_unpack_nested_types(field_type.get("fields", []), node))

            elif field_type.get("type", "") == "array":
                node["type"] = "array"
                node["valueType"] = field_type.get("elementType", "")
                _unpack_struct(node, field_type, "elementType")

            elif field_type.get("type", "") == "map":
                node["type"] = "map"
                node["keyType"] = field_type.get("keyType", "")
                node["valueType"] = field_type.get("valueType", "")
                _unpack_struct(node, field_type, "valueType")
        else:
            node["type"] = field_type
            records.append(node)

    return records
