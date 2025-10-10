"""Support for nested column types like: Array, Struct and Map."""

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional, Tuple

from pyspark.sql.types import DataType, StructType

from ons_metadata_validation.ids_common_utils.spark_datatype import (
    get_spark_datatype,
)
from ons_metadata_validation.processing.data_structures import Fail
from ons_metadata_validation.reference.constants import MetaMapper, SheetMapper


def evaluate_nested_columns(
    metadata_columns: Dict[str, Dict[str, Any]],
) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, str]]]:
    """Evaluate nested columns and converts the datatype to a spark datatype based on nesting.

    Args:
        metadata_columns (dict[str, dict[str, Any]]): _description_

    Returns:
        dict[str, dict[str, Any]]: _description_
    """
    errors = []
    errors.extend(validate_nesting_within_limit(metadata_columns.values()))
    nested_columns = create_nested_columns(metadata_columns.values())
    # modifies in place because it walks the tree
    errors.extend(convert_column_tree_datatypes(nested_columns))
    errors.extend(validate_parent_child_datatype(nested_columns))
    return unnest_columns(nested_columns), errors


def validate_nesting_within_limit(
    records: Iterable[Dict[str, Any]], max_nested_levels: int = 15
) -> List[Optional[Fail]]:
    """Validate the nesting is not beyond the max accepted.

    Args:
        records (list[dict[str, Any]]): Values of the metadata column records.
        max_nested_levels (int, optional): Max accepted nested levels. Defaults to 15.

    Returns:
        list[dict[Any, Any]]: _description_
    """

    def _validate_nesting_within_limit(variable: str) -> Optional[Fail]:
        nested_levels = variable.count(".")
        if nested_levels <= max_nested_levels:
            return None
        return Fail(
            "hard",
            SheetMapper.VARS.value,
            MetaMapper.VARS_variable_name.value,
            variable,
            f"Max nesting supported by BigQuery is {max_nested_levels}, got {nested_levels}.",
        )

    return list(
        filter(
            lambda x: x,
            map(
                lambda record: _validate_nesting_within_limit(
                    record[MetaMapper.VARS_variable_name.value]
                ),
                records,
            ),
        )
    )


def create_nested_columns(
    variables_records: Iterable[Dict[str, Any]],
) -> Dict[str, Dict]:
    """Create the schema for nested columns from the metadata template variables.

    Args:
        variables_records (list[dict[str, Any]]): The variable_df.to_dict("records") after the columns are renamed.

    Returns:
        dict[str, dict]: The nested schema.
    """

    def _insert_nested_column(metadata: Dict[str, Any]) -> None:
        """Insert a nested column into the schema from the metadata.

        Args:
            schema (dict[str, dict]): The nested schema to be updated in-place.
            metadata (dict[str, Any]): The metadata record for that row.
        """
        metadata = deepcopy(metadata)
        name = metadata[MetaMapper.VARS_variable_name.value]
        parts = metadata[MetaMapper.VARS_variable_name.value].split(".")
        current = schema

        # walk down to the second lowest nested level
        for idx, _ in enumerate(parts[:-1]):
            current = current[".".join(parts[: idx + 1])]["nested_columns"]  # type: ignore

        current[name] = {
            **metadata,
            "nested_columns": (
                {}
                if metadata[MetaMapper.VARS_variable_data_type.value]
                in ["map", "struct", "array"]
                else None
            ),
        }

    # sort by number of dots in name to get the outer types first
    variables_records = sorted(
        variables_records,
        key=lambda x: x.get(MetaMapper.VARS_variable_name.value, "").count("."),
    )

    schema: dict[str, Any] = {}
    for record in variables_records:
        _insert_nested_column(record)
    return schema


def convert_column_tree_datatypes(root: Dict) -> List[Fail]:
    """Walk over the nested column tree and convert the string datatypes to Spark datatypes.

    Args:
        root (dict): The root of the tree, this modifies in-place.

    """
    errors = []

    if isinstance(root, dict):
        for node in root.values():
            if isinstance(node, dict):
                convert_column_tree_datatypes(node)

                if MetaMapper.VARS_variable_data_type.value in node and node.get(
                    MetaMapper.VARS_variable_data_type.value
                ):
                    try:
                        node[MetaMapper.VARS_variable_data_type.value] = (
                            get_spark_datatype(**node)
                        )
                    except ValueError as e:
                        errors.append(
                            Fail(
                                "hard",
                                SheetMapper.VARS.value,
                                MetaMapper.VARS_variable_name.value,
                                node[MetaMapper.VARS_variable_name.value],
                                str(e),
                            )
                        )

        if "nested_columns" in root and root["nested_columns"]:
            possible_value_types = {}

            for child_name, child in root["nested_columns"].items():
                possible_value_types[child_name] = child[
                    MetaMapper.VARS_variable_data_type.value
                ]

            if root[MetaMapper.VARS_variable_data_type.value] == "struct" or isinstance(
                root[MetaMapper.VARS_variable_data_type.value], StructType
            ):
                try:
                    root[MetaMapper.VARS_variable_data_type.value] = get_spark_datatype(
                        **root
                    )
                except ValueError as e:
                    errors.append(
                        Fail(
                            "hard",
                            SheetMapper.VARS.value,
                            MetaMapper.VARS_variable_name.value,
                            root[MetaMapper.VARS_variable_name.value],
                            str(e),
                        )
                    )
            else:
                if len(set(possible_value_types.values())) == 1:
                    root[MetaMapper.VARS_value_data_type.value] = set(
                        possible_value_types.values()
                    ).pop()

                    if root.get(MetaMapper.VARS_key_data_type.value):
                        try:
                            root[MetaMapper.VARS_key_data_type.value] = (
                                get_spark_datatype(
                                    root[MetaMapper.VARS_key_data_type.value]
                                )
                            )
                        except ValueError as e:
                            errors.append(
                                Fail(
                                    "hard",
                                    SheetMapper.VARS.value,
                                    MetaMapper.VARS_variable_name.value,
                                    root[MetaMapper.VARS_variable_name.value],
                                    str(e),
                                )
                            )
                else:
                    errors.append(
                        Fail(
                            "hard",
                            SheetMapper.VARS.value,
                            MetaMapper.VARS_variable_name.value,
                            root[MetaMapper.VARS_variable_name.value],
                            f"Must not have multiple value data types in nested columns for type {root[MetaMapper.VARS_variable_data_type.value]}",
                        )
                    )
    return errors


def validate_parent_child_datatype(
    variables_nested_schema: Dict[str, Any],
) -> List[Dict[str, str]]:
    """Validate that parent value types are the same as the child datatype.

    Accepts both the string version of the datatypes and the spark types.

    Args:
        variables_nested_schema (dict[str, str  |  dict]): The nested columns data.

    Returns:
        list[dict[str, str]]: List of mismatches.
    """
    mismatches = []

    def validate_node(node, expected_type=None, path: str = ""):
        if node is None:
            return

        if (
            expected_type
            and node.get(MetaMapper.VARS_variable_data_type.value) != expected_type
        ):
            mismatches.append(
                Fail(
                    "hard",
                    SheetMapper.VARS.value,
                    MetaMapper.VARS_variable_name.value,
                    path,
                    f"Expected datatype '{expected_type}', got '{node.get(MetaMapper.VARS_variable_data_type.value)}'.",
                )
            )

        nested_cols = node.get("nested_columns", None)

        col_dtype = node.get(MetaMapper.VARS_variable_data_type.value)

        if isinstance(col_dtype, DataType):
            col_dtype = col_dtype.typeName()

        if nested_cols and col_dtype not in ["map", "struct", "array"]:
            mismatches.append(
                Fail(
                    "hard",
                    SheetMapper.VARS.value,
                    MetaMapper.VARS_variable_name.value,
                    path,
                    f"Datatype '{node.get(MetaMapper.VARS_variable_data_type.value)}' doesn't support nested columns.",
                )
            )

        if nested_cols:
            for nested_col_name, child_node in nested_cols.items():
                validate_node(
                    child_node,
                    node.get(MetaMapper.VARS_value_data_type.value),
                    nested_col_name,
                )

    for root_col, root_node in variables_nested_schema.items():
        validate_node(root_node, path=root_col)

    return mismatches


def unnest_columns(
    nested_schema: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Flatten nested structure to original shape.

    Args:
        nested_schema (dict[str, dict[str, Any]]): Nested schema.

    Returns:
        dict[str, dict[ str, Any]]: Schema in original shape.
    """
    flat_schema = {}

    def explore_node(root) -> None:
        for key, node in root.items():
            if node.get("nested_columns"):
                explore_node(node.get("nested_columns"))

            node.pop("nested_columns")
            flat_schema[key] = node

    explore_node(nested_schema)

    return dict(sorted(flat_schema.items()))
