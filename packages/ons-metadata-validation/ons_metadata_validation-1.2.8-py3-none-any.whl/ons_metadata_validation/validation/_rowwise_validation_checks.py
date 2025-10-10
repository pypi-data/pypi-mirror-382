import ons_metadata_validation.validation._validation_checks as vc
from ons_metadata_validation.reference.constants import (
    EMPTY_VALUES,
    MetaMapper,
)

# Dataset File tab rowwise checks


def must_have_format_matches_extension(row) -> bool:
    if not all(
        [
            isinstance(row[MetaMapper.FILE_file_path_and_name.value], str),
            isinstance(row[MetaMapper.FILE_file_format.value], str),
        ]
    ):
        return False
    return row[MetaMapper.FILE_file_path_and_name.value].endswith(
        row[MetaMapper.FILE_file_format.value].lower()
    )


def must_have_string_identifier_if_csv(row) -> bool:
    if not isinstance(row[MetaMapper.FILE_file_format.value], str):
        return False
    if row[MetaMapper.FILE_file_format.value].upper() != "CSV":
        return True
    return (
        row[MetaMapper.FILE_file_format.value].upper() == "CSV"
        and row[MetaMapper.FILE_string_identifier.value] not in EMPTY_VALUES
    )


def must_have_header_rows_if_csv(row) -> bool:
    if not isinstance(row[MetaMapper.FILE_file_format.value], str):
        return False
    if row[MetaMapper.FILE_file_format.value].upper() != "CSV":
        return True
    if not isinstance(row[MetaMapper.FILE_number_of_header_rows.value], int):
        return False
    return (
        row[MetaMapper.FILE_file_format.value].upper() == "CSV"
        and int(row[MetaMapper.FILE_number_of_header_rows.value]) >= 1
    )


def must_have_column_separator_if_csv(row, template: dict) -> bool:
    if not isinstance(row[MetaMapper.FILE_file_format.value], str):
        return False
    if row[MetaMapper.FILE_file_format.value].upper() != "CSV":
        return True
    return (
        row[MetaMapper.FILE_file_format.value].upper() == "CSV"
        and row[MetaMapper.FILE_column_seperator.value]
        in template[MetaMapper.FILE_column_seperator.value]["enum"]
    )


# Variables tabs rowwise checks
def must_have_description_that_is_not_variable_name(row) -> bool:
    if not isinstance(row[MetaMapper.VARS_variable_name.value], str) or not isinstance(
        row[MetaMapper.VARS_variable_description.value], str
    ):
        return True
    return (
        row[MetaMapper.VARS_variable_name.value].lower().strip()
        != row[MetaMapper.VARS_variable_description.value].lower().strip()
    )


def must_have_null_value_denoted_by_if_null(row) -> bool:
    if not isinstance(row[MetaMapper.VARS_nullability.value], str):
        return False
    if row[MetaMapper.VARS_nullability.value].upper() != "NULL":
        return True
    return row[
        MetaMapper.VARS_nullability.value
    ].upper() == "NULL" and vc.must_have_plausible_null_identifier(
        row[MetaMapper.VARS_null_values_denoted_by.value]
    )


def must_have_length_precision_if_decimal(row) -> bool:
    if not isinstance(row[MetaMapper.VARS_variable_data_type.value], str):
        return False
    if row[MetaMapper.VARS_variable_data_type.value].upper() != "DECIMAL":
        return True
    return row[
        MetaMapper.VARS_variable_data_type.value
    ].upper() == "DECIMAL" and vc.must_have_intelligible_length_precision(
        row[MetaMapper.VARS_variable_length_precision.value]
    )
