import ons_metadata_validation.validation._rowwise_validation_checks as rvc
from ons_metadata_validation.reference.constants import MetaMapper, SheetMapper
from ons_metadata_validation.reference.template import V2_TEMPLATE

# the first of the 2 is the independent condition
# second of the 2 in these row-wise checks is the value that is flagged to the user
# interface for this is (sheet, cols, func, fail_type, kwargs)
ROWWISE_VALIDATIONS = [
    (
        SheetMapper.FILE.value,
        [
            MetaMapper.FILE_file_path_and_name.value,
            MetaMapper.FILE_file_format.value,
        ],
        rvc.must_have_format_matches_extension,
        "hard_comparative",
        {},
    ),
    (
        SheetMapper.FILE.value,
        [
            MetaMapper.FILE_file_format.value,
            MetaMapper.FILE_column_seperator.value,
        ],
        rvc.must_have_column_separator_if_csv,
        "hard_comparative",
        {"template": V2_TEMPLATE},
    ),
    (
        SheetMapper.FILE.value,
        [
            MetaMapper.FILE_file_format.value,
            MetaMapper.FILE_string_identifier.value,
        ],
        rvc.must_have_string_identifier_if_csv,
        "hard_comparative",
        {},
    ),
    (
        SheetMapper.FILE.value,
        [
            MetaMapper.FILE_file_format.value,
            MetaMapper.FILE_number_of_header_rows.value,
        ],
        rvc.must_have_header_rows_if_csv,
        "hard_comparative",
        {},
    ),
    (
        SheetMapper.VARS.value,
        [
            MetaMapper.VARS_variable_name.value,
            MetaMapper.VARS_variable_description.value,
        ],
        rvc.must_have_description_that_is_not_variable_name,
        "soft_comparative",
        {},
    ),
    (
        SheetMapper.VARS.value,
        [
            MetaMapper.VARS_nullability.value,
            MetaMapper.VARS_null_values_denoted_by.value,
        ],
        rvc.must_have_null_value_denoted_by_if_null,
        "soft_comparative",
        {},
    ),
    (
        SheetMapper.VARS.value,
        [
            MetaMapper.VARS_variable_data_type.value,
            MetaMapper.VARS_variable_length_precision.value,
        ],
        rvc.must_have_length_precision_if_decimal,
        "hard_comparative",
        {},
    ),
]
