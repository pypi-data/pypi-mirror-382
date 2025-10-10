from typing import Any, Dict

from pyspark.sql.types import (
    ArrayType,
    BooleanType,
    ByteType,
    DataType,
    DataTypeSingleton,
    DateType,
    DecimalType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    MapType,
    ShortType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from ons_metadata_validation.reference.constants import MetaMapper

# Tuple of all PySpark data types
pyspark_data_types = (
    StringType,
    IntegerType,
    LongType,
    DoubleType,
    DecimalType,
    DateType,
    TimestampType,
    BooleanType,
    ArrayType,
    MapType,
    StructType,
    FloatType,
    ByteType,
    ShortType,
)


def is_pyspark_data_type(obj):
    """Check if an object is a supported spark type."""
    return isinstance(obj, pyspark_data_types)


def get_spark_datatype(data_type: Any = None, /, **kwargs) -> DataType:
    """Return the equivalent spark data type from a string representation of common data types.

    Args:
        data_type (Any, optional): Single value column data type. Defaults to None.
        kwargs (dict[str, Any]): The json representation of a column to unpack.

    Returns:
        DataType: The resulting spark data type
    """
    if kwargs.get(MetaMapper.VARS_variable_data_type.value):
        data_type = kwargs.get(MetaMapper.VARS_variable_data_type.value)

    # Check if the input is already a Spark data type
    if is_pyspark_data_type(data_type):
        return data_type

    # Check if the input is an uninitialised Spark type
    if isinstance(data_type, DataTypeSingleton):
        data_type = data_type.__name__

    # Check if the input is a Spark type
    if isinstance(data_type, DataType):
        data_type = data_type.typeName()

    # Check if the input is a tuple for DecimalType
    if isinstance(data_type, tuple) and isinstance(
        get_spark_datatype(data_type[0]), DecimalType
    ):
        return DecimalType(int(data_type[1]), int(data_type[2]))

    if not isinstance(data_type, str):
        raise TypeError(f"data_type must be a string, got {type(data_type)}")

    if not data_type.strip():  # Check for empty string
        raise ValueError("data_type cannot be an empty string.")

    data_type_mapping = {
        "ARRAY": ArrayType,  # return uninitialised version for V3 metadata template
        "BIGINT": LongType(),
        "BOOLEAN": BooleanType(),
        "CLOB": StringType(),
        "DATE": DateType(),
        "DATETIME": TimestampType(),
        "DECIMAL": DecimalType,  # return uninitialised version for V3 metadata template
        "DOUBLE": DoubleType(),
        "FLOAT": DoubleType(),
        "INT": LongType(),  # Changed to LongType()
        "INTEGER": LongType(),  # Changed to LongType()
        "INT8": LongType(),
        "INT16": LongType(),
        "INT32": LongType(),
        "INT64": LongType(),
        "LONG": LongType(),
        "LONGTEXT": StringType(),
        "MAP": MapType,  # return uninitialised version for V3 metadata template
        "SHORTTEXT": StringType(),
        "SMALLINT": IntegerType(),
        "STRING": StringType(),
        "STRINGTYPE": StringType(),  # Added
        "STR": StringType(),
        "STRUCT": StructType,  # return uninitialised version for V3 metadata template
        "TEXT": StringType(),
        "TIME": TimestampType(),
        "TIMESTAMP": TimestampType(),
        "TINYINT": IntegerType(),
        "UNICODESTRING": StringType(),
        # legacy types we want to support for migration
        "FLOATTYPE": FloatType(),
        "BYTETYPE": ByteType(),
        "SHORTTYPE": ShortType(),
    }

    # include spark types in keys
    data_type_mapping = {
        **data_type_mapping,
        **{
            str(v).split(".")[-1].strip("'>()").upper(): v
            for k, v in data_type_mapping.items()
        },
    }

    mapped_data_type = data_type_mapping.get(data_type.strip().upper())

    if mapped_data_type is None:
        raise ValueError(f"Data type '{data_type}' not found.")
    data_type = mapped_data_type

    if data_type == ArrayType:
        if not kwargs.get(MetaMapper.VARS_value_data_type.value):
            raise ValueError(
                f"ArrayType must contain one element type. Got: {kwargs.get(MetaMapper.VARS_value_data_type.value)}"
            )
        return ArrayType(
            get_spark_datatype(kwargs.get(MetaMapper.VARS_value_data_type.value)),
            kwargs.get(MetaMapper.VARS_nullability.value, True),
        )

    if data_type == MapType:
        if not (
            kwargs.get(MetaMapper.VARS_key_data_type.value)
            and kwargs.get(MetaMapper.VARS_value_data_type.value)
        ):
            raise ValueError(
                "MapType must contain exactly two types for key and value. "
                f"Got: key = {kwargs.get(MetaMapper.VARS_key_data_type.value)}, value = {kwargs.get(MetaMapper.VARS_value_data_type.value)}"
            )
        return MapType(
            get_spark_datatype(kwargs.get(MetaMapper.VARS_key_data_type.value)),
            get_spark_datatype(kwargs.get(MetaMapper.VARS_value_data_type.value)),
            kwargs.get(MetaMapper.VARS_nullability.value, True),
        )

    if data_type == StructType:
        if not kwargs.get("nested_columns"):
            raise ValueError(
                "No nested_columns given, cannot create StructFields for StructType"
            )
        return StructType(
            [
                StructField(
                    k.split(".")[-1],
                    get_spark_datatype(**v),
                    v.get(MetaMapper.VARS_nullability.value, True),
                )
                for k, v in kwargs.get("nested_columns").items()  # type: ignore[union-attr]
            ]
        )

    if data_type == DecimalType:
        if not (kwargs.get(MetaMapper.VARS_variable_length_precision.value)):
            # warnings.warn(
            #     "DecimalType must contain precision and scale. Using Spark default (10, 0). "
            #     f"Got: column_precision = {kwargs.get('column_precision')}, column_scale = {kwargs.get('column_scale')}"
            # )
            return DecimalType()
        precision, scale = map(
            int,
            str(kwargs.get(MetaMapper.VARS_variable_length_precision.value)).split(","),
        )
        return DecimalType(precision, scale)  # type: ignore[arg-type]

    if isinstance(data_type, DataType):
        return data_type
    else:
        raise ValueError(
            f"Only one type can be passed at a time, apart from Map or Array. Got {data_type}, {kwargs}"
        )


def build_spark_schema_from_json(
    json_columns: Dict[str, Dict[str, Any]],
) -> StructType:
    """Build spark schema from json columns.
    Args:
        json_columns (Dict[str, Dict[str, Any]]): JSON columns from converted metadata.
    Returns:
        StructType: The spark schema generated from the metadata template.
    """
    # we already have what we need from the nested columns in the schema so don't need the fields with a "." in
    # use get_spark_datatype in case conversion hasn't already happened - this should only be possible with V2 template \
    # because we need the nested structure to be validated and built for V3+ template.
    try:
        return StructType(
            [
                StructField(
                    node[MetaMapper.VARS_variable_name.value],
                    get_spark_datatype(**node),
                    node[MetaMapper.VARS_nullability.value],
                )
                for name, node in json_columns.items()
                if "." not in name
            ]
        )
    except (ValueError, TypeError) as e:
        print(e)
        return StructType([])
