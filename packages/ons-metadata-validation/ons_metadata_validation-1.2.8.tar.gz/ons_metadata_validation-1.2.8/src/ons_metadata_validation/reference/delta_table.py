"""
Add changes here, all are run sequentially so v2.1 is run then v2.2 etc

DELTA_TABLE = {
    "v2.1": {
        "DatasetFile_column_seperator": {
            "name": "Column Separator",
        }
    }
    # if we made a mistake and reverted back to the original spelling
    # the changes would be applied
    "v2.2": {
        "DatasetFile_column_seperator": {
            "name": "Column Seperator",
        }
    }
}

empty dict means nothing is changed
key: None means the value is removed
"""

from ons_metadata_validation.reference.constants import DATA_TYPES, MetaMapper

# UPDATE_WITH_VERSION
# if a value is removed update with {key}: None
DELTA_TABLE = {
    3.0: {
        # "PARQUET" -> "Parquet"
        # the pipeline uppers the string so we accept both
        MetaMapper.FILE_file_format.value: {
            "enum": ["CSV", "JSON", "Parquet", "PARQUET", "JSON Multi-Line"]
        },
        MetaMapper.FILE_column_seperator.value: {
            "name": "Column Separator",
        },
        MetaMapper.FILE_is_this_file_one_of_a_sequence_to_be_appended_back_together.value: None,
        # Dataset file column O onwards shift left 1 due to deleted variable
        MetaMapper.FILE_number_of_header_rows.value: {
            "ref_cell": "N7",
            "value_cell": "N11",
        },
        MetaMapper.FILE_number_of_footer_rows.value: {
            "ref_cell": "O7",
            "value_cell": "O11",
        },
        MetaMapper.FILE_character_encoding.value: {
            "ref_cell": "P7",
            "value_cell": "P11",
        },
        MetaMapper.FILE_hash_value_for_checksum.value: {
            "ref_cell": "Q7",
            "value_cell": "Q11",
        },
        MetaMapper.FILE_notes.value: {
            "ref_cell": "R7",
            "value_cell": "R11",
        },
        # New variable
        MetaMapper.VARS_variable_availability.value: {
            "tab": "Variables",
            "name": "Variable availability",
            "ref_cell": "J6",
            "value_cell": "J10",
            "mandatory": True,
            "enum": ["Standard", "On request"],
            "datatype": str,
            "std_name": MetaMapper.VARS_variable_availability.value,
        },
        # New variable
        MetaMapper.VARS_row_level_restrictions.value: {
            "tab": "Variables",
            "name": "Row-level restrictions",
            "ref_cell": "K6",
            "value_cell": "K10",
            "mandatory": True,
            "enum": ["No", "Yes"],
            "datatype": str,
            "std_name": MetaMapper.VARS_row_level_restrictions.value,
        },
        MetaMapper.VARS_gcp_data_type.value: None,
        # Note that excel field is free text, but only certain values are
        # actually accepted by the pipeline
        # Also note the list is currently the same in all three cases...
        # ...but that might change in future if spark has opinions
        MetaMapper.VARS_variable_data_type.value: {
            "name": "Variable data type",
            "ref_cell": "L6",
            "value_cell": "L10",
            "enum": DATA_TYPES,
        },
        # New variable
        MetaMapper.VARS_key_data_type.value: {
            "tab": "Variables",
            "name": "Key data type",
            "ref_cell": "M6",
            "value_cell": "M10",
            "mandatory": False,
            "enum": DATA_TYPES,
            "datatype": str,
            "std_name": MetaMapper.VARS_key_data_type.value,
        },
        # New variable
        MetaMapper.VARS_value_data_type.value: {
            "tab": "Variables",
            "name": "Value data type",
            "ref_cell": "N6",
            "value_cell": "N10",
            "mandatory": False,
            "enum": DATA_TYPES,
            "datatype": str,
            "std_name": MetaMapper.VARS_value_data_type.value,
        },
        # Columns shift right due to new columns
        # This one is renamed because we're no longer asking for string length
        MetaMapper.VARS_variable_length_precision.value: {
            "name": "Variable precision/scale",
            "ref_cell": "O6",
            "value_cell": "O10",
        },
        MetaMapper.VARS_variable_format.value: {
            "ref_cell": "P6",
            "value_cell": "P10",
        },
        MetaMapper.VARS_is_primary_key.value: {
            "mandatory": True,
            "ref_cell": "Q6",
            "value_cell": "Q10",
        },
        MetaMapper.VARS_is_foreign_key.value: {
            "ref_cell": "R6",
            "value_cell": "R10",
        },
        MetaMapper.VARS_foreign_key_file_name.value: {
            "ref_cell": "S6",
            "value_cell": "S10",
        },
        MetaMapper.VARS_foreign_key_variable_name.value: {
            "ref_cell": "T6",
            "value_cell": "T10",
        },
        MetaMapper.VARS_nullability.value: {
            "ref_cell": "U6",
            "value_cell": "U10",
        },
        MetaMapper.VARS_null_values_denoted_by.value: {
            "ref_cell": "V6",
            "value_cell": "V10",
        },
        MetaMapper.VARS_variable_constraints.value: {
            "ref_cell": "W6",
            "value_cell": "W10",
        },
        MetaMapper.VARS_applicable_business_rules.value: {
            "ref_cell": "X6",
            "value_cell": "X10",
        },
        MetaMapper.VARS_is_this_a_code.value: {
            "ref_cell": "Y6",
            "value_cell": "Y10",
        },
        MetaMapper.VARS_notes.value: {
            "ref_cell": "Z6",
            "value_cell": "Z10",
        },
        # New variable
        MetaMapper.DATASET_frequency_of_collection.value: {
            "tab": "Back Office",
            "name": "Frequency of Collection",
            "ref_cell": "C20",
            "value_cell": "F20",
            "mandatory": True,
            "enum": [
                "Annual",
                "Biennial",
                "Bimonthly",
                "Biweekly",
                "Continuous",
                "Daily",
                "Historical",
                "Irregular",
                "Monthly",
                "Periodic",
                "Quarterly",
                "Real Time",
                "Semiannual",
                "Semimonthly",
                "Semiweekly",
                "Single",
                "Three times a month",
                "Three times a week",
                "Three times a year",
                "Triennial",
                "Weekly",
            ],
            "datatype": str,
            "std_name": MetaMapper.DATASET_frequency_of_collection.value,
        },
        # Shift of meaning of existing variable
        # Same enum list as above (and as before) - could define as constant
        # Also, rows shift down by 1 due to new variable
        MetaMapper.DATASET_frequency.value: {
            "name": "Frequency of Delivery",
            "ref_cell": "C21",
            "value_cell": "F21",
        },
        MetaMapper.DATASET_geographic_coverage.value: {
            "ref_cell": "C22",
            "value_cell": "F22",
        },
        MetaMapper.DATASET_temporal_coverage.value: {
            "ref_cell": "C23",
            "value_cell": "F23",
        },
        MetaMapper.DATASET_sensitivity_status_for_dataset_resource.value: {
            "ref_cell": "C24",
            "value_cell": "F24",
        },
        MetaMapper.DATASET_sensitivity_tool_url.value: {
            "ref_cell": "C25",
            "value_cell": "F25",
        },
        MetaMapper.DATASET_retention_date.value: {
            "ref_cell": "C26",
            "value_cell": "F26",
        },
        MetaMapper.DATASET_provider_statement_for_retention_removal_or_deletion.value: {
            "ref_cell": "C27",
            "value_cell": "F27",
        },
        MetaMapper.DATASET_removal_date.value: {
            "ref_cell": "C28",
            "value_cell": "F28",
        },
        MetaMapper.DATASET_removal_comments.value: {
            "ref_cell": "C29",
            "value_cell": "F29",
        },
        MetaMapper.DATASET_data_controller.value: {
            "ref_cell": "C30",
            "value_cell": "F30",
        },
        MetaMapper.DATASET_data_processor.value: {
            "ref_cell": "C31",
            "value_cell": "F31",
        },
        MetaMapper.DATASET_licensing_status.value: {
            "mandatory": True,
        },
        MetaMapper.DATASET_geographic_level.value: {
            "mandatory": True,
        },
        MetaMapper.DATASET_other_unique_identifier_s_for_dataset_resource.value: {
            "mandatory": True,
        },
        MetaMapper.DATASET_dataset_domain.value: None,
        # Now that we're +1 and -1 variable, there's no offset for a while
        # Ampersand replace with 'and'
        MetaMapper.DATASET_metadata_access.value: {
            "enum": [
                "Publish to Website and Hub",
                "Publish to Hub only",
                "Do not publish",
            ]
        },
        # Renamed to clarify that the Q is about the metadata, not the data itself
        MetaMapper.DATASET_should_this_dataset_be_visible_for_internal_or_external_users.value: {
            "name": "Should the information about this dataset be visible for internal or external users?",
        },
        # New variable
        # TODO: if this is indeed a multiselect, will need to turn off enum and write custom
        # multi-select combinations check
        MetaMapper.DATASET_safe_settings.value: {
            "tab": "Back Office",
            "name": "Safe Settings",
            "ref_cell": "C45",
            "value_cell": "F45",
            "mandatory": True,
            "enum": [
                "ESRC SafePods",
                "Assured Organisational Connectivity (office-based)",
                "Assured Organisational Connectivity (homeworking)",
                "ESRC SafePods, Assured Organisational Connectivity (office-based)",
                "ESRC SafePods, Assured Organisational Connectivity (homeworking)",
                "Assured Organisational Connectivity (office-based), ESRC SafePods",
                "Assured Organisational Connectivity (office-based), Assured Organisational Connectivity (homeworking)",
                "Assured Organisational Connectivity (homeworking), ESRC SafePods",
                "Assured Organisational Connectivity (homeworking), Assured Organisational Connectivity (office-based)",
                "ESRC SafePods, Assured Organisational Connectivity (office-based), Assured Organisational Connectivity (homeworking)",
                "ESRC SafePods, Assured Organisational Connectivity (homeworking), Assured Organisational Connectivity (office-based)",
                "Assured Organisational Connectivity (office-based), ESRC SafePods, Assured Organisational Connectivity (homeworking)",
                "Assured Organisational Connectivity (office-based), Assured Organisational Connectivity (homeworking), ESRC SafePods",
                "Assured Organisational Connectivity (homeworking), ESRC SafePods, Assured Organisational Connectivity (office-based)",
                "Assured Organisational Connectivity (homeworking), Assured Organisational Connectivity (office-based), ESRC SafePods",
            ],
            "datatype": str,
            "std_name": MetaMapper.DATASET_safe_settings.value,
        },
        MetaMapper.DATASET_access_level.value: {
            "tab": "Back Office",
            "name": "Access Level",
            "ref_cell": "C46",
            "value_cell": "F46",
            "mandatory": True,
            "enum": [
                "Access level 1",
                "Access level 2",
                "Access level 3",
            ],
            "datatype": str,
            "std_name": MetaMapper.DATASET_access_level.value,
        },
        MetaMapper.DATASET_subject_to_low_level_access_control.value: {
            "tab": "Back Office",
            "name": "Subject to Low Level Access Control",
            "ref_cell": "C47",
            "value_cell": "F47",
            "mandatory": True,
            "enum": ["No", "Yes"],
            "datatype": str,
            "std_name": MetaMapper.DATASET_subject_to_low_level_access_control.value,
        },
    }
}
