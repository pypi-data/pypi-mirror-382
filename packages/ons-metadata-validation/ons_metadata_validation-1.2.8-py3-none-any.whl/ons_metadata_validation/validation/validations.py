import ons_metadata_validation.validation._validation_checks as vc
from ons_metadata_validation.reference.constants import MetaMapper

STRING_HYGIENE_CHECKS = [
    vc.must_not_start_with_whitespace,
    vc.must_not_end_with_whitespace,
    vc.must_not_contain_double_spaces,
]

# validations for multi tab variables
DATA_CREATOR_VALIDATIONS = {
    "hard": [vc.must_not_include_apostrophes, *STRING_HYGIENE_CHECKS],
    "soft": [
        vc.must_have_no_obvious_acronyms,
        vc.must_not_say_ONS,
        vc.must_not_say_office_of_national_statistics,
        vc.must_not_have_capitalised_for,
    ],
}

GCP_BQ_TABLE_NAME_VALIDATIONS = {
    "hard": [
        vc.must_be_alphanumeric_with_underscores,
        vc.must_be_all_lower_case,
        vc.must_not_start_with_digit,
        vc.must_be_within_length_30,
        *STRING_HYGIENE_CHECKS,
    ]
}

GCP_BQ_VARIABLE_NAME_VALIDATIONS = {
    "hard": [
        vc.must_be_alphanumeric_with_underscores_and_dot,
        vc.must_be_within_length_300,
        vc.must_not_start_with_digit,
        *STRING_HYGIENE_CHECKS,
    ],
    "soft": [vc.must_be_all_lower_case],
}

DATASET_SERIES_DESC_VALIDATIONS = {
    "hard": [
        vc.must_not_include_illegal_quote_characters,
        vc.must_be_within_length_1800,
        *STRING_HYGIENE_CHECKS,
    ],
    "soft": [
        vc.must_end_with_a_full_stop_or_question_mark,
        vc.must_have_no_obvious_acronyms,
    ],
}

DATASET_SERIES_REF_PERIOD_VALIDATIONS = {
    "hard": [
        vc.must_be_in_long_date_format,
        vc.must_have_no_leading_apostrophe,
        *STRING_HYGIENE_CHECKS,
    ],
    "soft": [vc.must_have_long_date_in_plausible_range],
}

NOTES_VALIDATIONS = {"soft": [*STRING_HYGIENE_CHECKS, vc.must_be_within_length_1800]}

SOFT_STRING_HYGIENE = {"soft": [*STRING_HYGIENE_CHECKS]}


# single value validations
SINGLE_VALUE_VALIDATIONS = {
    MetaMapper.DATASET_dataset_resource_name.value: {
        "hard": [
            vc.must_be_alphanumeric_with_spaces_dots_or_commas,
            *STRING_HYGIENE_CHECKS,
        ],
        "soft": [
            vc.must_have_no_obvious_acronyms,
            vc.must_be_within_length_80,
        ],
    },
    MetaMapper.DATASET_acronym.value: {
        "hard": [*STRING_HYGIENE_CHECKS],
        "soft": [
            vc.must_have_no_full_stops_in_acronym,
            vc.must_not_include_spaces,
        ],
    },
    MetaMapper.DATASET_significant_changes.value: SOFT_STRING_HYGIENE,
    MetaMapper.DATASET_data_creator.value: DATA_CREATOR_VALIDATIONS,
    MetaMapper.DATASET_data_contributor_s.value: DATA_CREATOR_VALIDATIONS,
    MetaMapper.DATASET_purpose_of_this_dataset_resource.value: SOFT_STRING_HYGIENE,
    MetaMapper.DATASET_search_keywords.value: {
        "hard": [*STRING_HYGIENE_CHECKS],
        "soft": [
            vc.must_not_include_pipes,
            vc.must_start_with_capital,
            vc.must_have_no_more_than_five_list_items,
            vc.must_have_caps_after_commas,
        ],
    },
    MetaMapper.DATASET_dataset_theme.value: {},
    MetaMapper.DATASET_geographic_level.value: SOFT_STRING_HYGIENE,
    MetaMapper.DATASET_provenance.value: {
        "hard": [*STRING_HYGIENE_CHECKS],
        "soft": [vc.must_not_be_option_from_dataset_resource_type],
    },
    MetaMapper.DATASET_number_of_dataset_series.value: {
        "hard": [vc.must_be_1_or_greater]
    },
    MetaMapper.DATASET_number_of_structural_data_files.value: {
        "hard": [vc.must_be_1_or_greater]
    },
    MetaMapper.DATASET_date_of_completion.value: {
        "hard": [
            vc.must_be_in_short_date_format,
            vc.must_have_leading_apostrophe,
            *STRING_HYGIENE_CHECKS,
        ],
        "soft": [vc.must_have_short_date_in_plausible_range],
    },
    MetaMapper.DATASET_name_and_email_of_individual_completing_this_template.value: {
        "hard": [
            vc.must_contain_an_email_address,
            vc.must_have_comma_and_space,
            *STRING_HYGIENE_CHECKS,
        ]
    },
    MetaMapper.DATASET_security_classification.value: {},
    MetaMapper.DATASET_dataset_resource_type.value: {},
    MetaMapper.DATASET_number_of_non_structural_reference_files.value: {
        "hard": [vc.must_be_0_or_greater]
    },
    MetaMapper.DATASET_number_of_code_list_files.value: {
        "hard": [vc.must_be_0_or_greater]
    },
    MetaMapper.SERIES_dataset_series_name.value: {
        "hard": [
            vc.must_be_alphanumeric_with_spaces,
            vc.must_not_start_with_digit,
            vc.must_be_within_length_1024,
            *STRING_HYGIENE_CHECKS,
        ]
    },
    MetaMapper.SERIES_google_cloud_platform_bigquery_table_name.value: GCP_BQ_TABLE_NAME_VALIDATIONS,
    MetaMapper.SERIES_description.value: DATASET_SERIES_DESC_VALIDATIONS,
    MetaMapper.SERIES_reference_period.value: DATASET_SERIES_REF_PERIOD_VALIDATIONS,
    MetaMapper.SERIES_geographic_coverage.value: SOFT_STRING_HYGIENE,
    MetaMapper.SERIES_frequency.value: {},
    MetaMapper.SERIES_supply_type.value: {},
    MetaMapper.SERIES_wave_number_time_period_covered_survey_only.value: SOFT_STRING_HYGIENE,
    MetaMapper.SERIES_links_to_online_documentation_and_other_useful_materials.value: {
        "hard": [*STRING_HYGIENE_CHECKS],
        "soft": [vc.must_be_valid_url],
    },
    MetaMapper.FILE_google_cloud_platform_bigquery_table_name.value: GCP_BQ_TABLE_NAME_VALIDATIONS,
    MetaMapper.FILE_file_path_and_name.value: {
        "hard": [vc.must_not_include_backslashes, *STRING_HYGIENE_CHECKS],
        "soft": [
            vc.must_have_timestamp_in_filename,
            vc.must_have_plausible_filepath,
        ],
    },
    MetaMapper.FILE_file_format.value: {},
    MetaMapper.FILE_column_seperator.value: {},
    MetaMapper.FILE_string_identifier.value: SOFT_STRING_HYGIENE,
    MetaMapper.FILE_file_description.value: SOFT_STRING_HYGIENE,
    MetaMapper.FILE_reference_period.value: {},
    MetaMapper.FILE_file_size.value: {},
    MetaMapper.FILE_file_size_unit.value: {
        "hard": [
            vc.must_have_intelligible_file_size_unit,
            *STRING_HYGIENE_CHECKS,
        ]
    },
    MetaMapper.FILE_is_code_list.value: {},
    MetaMapper.FILE_number_of_records.value: {"hard": [vc.must_be_0_or_greater]},
    MetaMapper.FILE_is_this_file_one_of_a_sequence_to_be_appended_back_together.value: {},
    MetaMapper.FILE_number_of_header_rows.value: {"hard": [vc.must_be_0_or_greater]},
    MetaMapper.FILE_number_of_footer_rows.value: {"hard": [vc.must_be_0_or_greater]},
    MetaMapper.FILE_character_encoding.value: {
        "hard": [vc.must_be_valid_encoding, *STRING_HYGIENE_CHECKS]
    },
    MetaMapper.FILE_hash_value_for_checksum.value: {
        "hard": [
            vc.must_be_alphanumeric_only,
            vc.must_be_exactly_32_chars,
            *STRING_HYGIENE_CHECKS,
        ]
    },
    MetaMapper.FILE_notes.value: NOTES_VALIDATIONS,
    MetaMapper.VARS_google_cloud_platform_bigquery_table_name.value: GCP_BQ_TABLE_NAME_VALIDATIONS,
    MetaMapper.VARS_variable_name.value: GCP_BQ_VARIABLE_NAME_VALIDATIONS,
    MetaMapper.VARS_google_cloud_platform_compatible_variable_name.value: GCP_BQ_VARIABLE_NAME_VALIDATIONS,
    MetaMapper.VARS_variable_label.value: {
        "hard": [
            vc.must_be_alphanumeric_with_spaces,
            vc.must_be_within_length_300,
            *STRING_HYGIENE_CHECKS,
        ]
    },
    MetaMapper.VARS_variable_description.value: {
        "hard": [vc.must_be_within_length_1024, *STRING_HYGIENE_CHECKS],
        "soft": [vc.must_end_with_a_full_stop_or_question_mark],
    },
    MetaMapper.VARS_position_in_file.value: {"hard": [vc.must_be_1_or_greater]},
    MetaMapper.VARS_personally_identifiable_information.value: {},
    MetaMapper.VARS_variable_data_type.value: {
        "hard": [vc.must_be_valid_datatype, *STRING_HYGIENE_CHECKS]
    },
    MetaMapper.VARS_gcp_data_type.value: {
        "hard": [*STRING_HYGIENE_CHECKS],
        "soft": [vc.must_be_valid_gcp_datatype],
    },
    MetaMapper.VARS_variable_length_precision.value: {
        "hard": [
            vc.must_not_talk_in_terms_of_decimal_places,
            *STRING_HYGIENE_CHECKS,
        ]
    },
    MetaMapper.VARS_variable_format.value: {
        "hard": [
            vc.must_resemble_a_date_format_specification,
            *STRING_HYGIENE_CHECKS,
        ]
    },
    MetaMapper.VARS_is_primary_key.value: {},
    MetaMapper.VARS_is_foreign_key.value: {},
    MetaMapper.VARS_foreign_key_file_name.value: {},
    MetaMapper.VARS_foreign_key_variable_name.value: {},
    MetaMapper.VARS_nullability.value: {},
    MetaMapper.VARS_null_values_denoted_by.value: {},
    MetaMapper.VARS_variable_constraints.value: SOFT_STRING_HYGIENE,
    MetaMapper.VARS_applicable_business_rules.value: SOFT_STRING_HYGIENE,
    MetaMapper.VARS_is_this_a_code.value: {},
    MetaMapper.VARS_notes.value: NOTES_VALIDATIONS,
    MetaMapper.CODES_google_cloud_platform_bigquery_table_name.value: GCP_BQ_TABLE_NAME_VALIDATIONS,
    MetaMapper.CODES_variable_name.value: GCP_BQ_VARIABLE_NAME_VALIDATIONS,
    MetaMapper.CODES_key.value: {},
    MetaMapper.CODES_value.value: {},
    MetaMapper.CODES_notes.value: NOTES_VALIDATIONS,
    MetaMapper.DATASET_ids_business_catalogue_identifier.value: {
        "hard": [vc.must_be_zero_dot_followed_by_four_digits]
    },
    MetaMapper.DATASET_description.value: DATASET_SERIES_DESC_VALIDATIONS,
    MetaMapper.DATASET_abstract.value: {
        "hard": [
            vc.must_be_within_length_160,
            vc.must_end_with_a_full_stop_or_question_mark,
            *STRING_HYGIENE_CHECKS,
        ]
    },
    MetaMapper.DATASET_google_cloud_platform_project_name.value: {
        "hard": [
            vc.must_be_alphanumeric_with_dashes,
            vc.must_be_all_lower_case,
            vc.must_be_within_length_1024,
            vc.must_not_start_with_digit,
            *STRING_HYGIENE_CHECKS,
        ],
        "soft": [vc.must_be_poc_pipe_prod],
    },
    MetaMapper.DATASET_google_cloud_platform_big_query_dataset_name.value: {
        "hard": [
            vc.must_be_alphanumeric_with_underscores,
            vc.must_be_all_lower_case,
            vc.must_be_within_length_80,
            vc.must_not_start_with_digit,
            *STRING_HYGIENE_CHECKS,
        ]
    },
    MetaMapper.DATASET_other_unique_identifier_s_for_dataset_resource.value: {},
    MetaMapper.DATASET_frequency.value: {},
    MetaMapper.DATASET_geographic_coverage.value: {},
    MetaMapper.DATASET_temporal_coverage.value: DATASET_SERIES_REF_PERIOD_VALIDATIONS,
    MetaMapper.DATASET_sensitivity_status_for_dataset_resource.value: {},
    MetaMapper.DATASET_sensitivity_tool_url.value: {
        "hard": [vc.must_be_valid_url, *STRING_HYGIENE_CHECKS]
    },
    MetaMapper.DATASET_retention_date.value: {
        "hard": [
            vc.must_be_in_short_date_format,
            vc.must_have_leading_apostrophe,
            *STRING_HYGIENE_CHECKS,
        ],
        "soft": [vc.must_be_date_in_future],
    },
    MetaMapper.DATASET_provider_statement_for_retention_removal_or_deletion.value: SOFT_STRING_HYGIENE,
    MetaMapper.DATASET_removal_date.value: {
        "hard": [
            vc.must_be_in_short_date_format,
            vc.must_have_leading_apostrophe,
            *STRING_HYGIENE_CHECKS,
        ],
        "soft": [vc.must_be_date_in_past],
    },
    MetaMapper.DATASET_removal_comments.value: SOFT_STRING_HYGIENE,
    MetaMapper.DATASET_data_controller.value: {
        "hard": [*STRING_HYGIENE_CHECKS],
        "soft": [vc.must_have_no_obvious_acronyms],
    },
    MetaMapper.DATASET_data_processor.value: {
        "hard": [*STRING_HYGIENE_CHECKS],
        "soft": [vc.must_have_no_obvious_acronyms],
    },
    MetaMapper.DATASET_dataset_domain.value: {},
    MetaMapper.DATASET_legal_gateway.value: {},
    MetaMapper.DATASET_other_legal_gateway.value: SOFT_STRING_HYGIENE,
    MetaMapper.DATASET_licensing_status.value: {},
    MetaMapper.DATASET_metadata_access.value: {},
    MetaMapper.DATASET_documentation.value: {
        "hard": [
            vc.must_be_valid_url,
            vc.must_not_be_ons_sharepoint_url,
            vc.must_not_contain_more_than_one_url,
            *STRING_HYGIENE_CHECKS,
        ]
    },
    MetaMapper.DATASET_what_are_the_linkage_requirements_for_the_data_within_the_project_scope.value: SOFT_STRING_HYGIENE,
    MetaMapper.DATASET_how_has_deidentification_been_achieved.value: SOFT_STRING_HYGIENE,
    MetaMapper.DATASET_should_this_dataset_be_visible_for_internal_or_external_users.value: {},
    MetaMapper.DATASET_restrictions_for_access.value: {},
    MetaMapper.DATASET_research_outputs.value: {},
    MetaMapper.DATASET_project_approval.value: {},
    MetaMapper.DATASET_disclosure_control.value: {},
    MetaMapper.DATASET_research_disclaimer.value: {},
    # added fields in V3
    MetaMapper.VARS_variable_availability.value: {},
    MetaMapper.VARS_row_level_restrictions.value: {},
    MetaMapper.VARS_key_data_type.value: {},
    MetaMapper.VARS_value_data_type.value: {},
    MetaMapper.DATASET_frequency_of_collection.value: {},
    MetaMapper.DATASET_safe_settings.value: {},
    MetaMapper.DATASET_access_level.value: {},
    MetaMapper.DATASET_subject_to_low_level_access_control.value: {},
}
