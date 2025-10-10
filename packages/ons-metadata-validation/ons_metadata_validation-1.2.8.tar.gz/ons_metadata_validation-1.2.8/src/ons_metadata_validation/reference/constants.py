from enum import Enum
from typing import Dict, Union

import numpy as np

from ons_metadata_validation.processing.data_structures import TabDetails


class SheetMapper(Enum):
    RESOURCE = "Dataset Resource"
    SERIES = "Dataset Series"
    FILE = "Dataset File"
    VARS = "Variables"
    CODES = "Codes and Values"
    BACK_OFFICE = "Back Office"
    CHANGE_HISTORY = "Change history"


class MetaMapper(Enum):
    DATASET_dataset_resource_name = "DATASET_dataset_resource_name"
    DATASET_acronym = "DATASET_acronym"
    DATASET_significant_changes = "DATASET_significant_changes"
    DATASET_data_creator = "DATASET_data_creator"
    DATASET_data_contributor_s = "DATASET_data_contributor_s"
    DATASET_purpose_of_this_dataset_resource = (
        "DATASET_purpose_of_this_dataset_resource"
    )
    DATASET_search_keywords = "DATASET_search_keywords"
    DATASET_dataset_theme = "DATASET_dataset_theme"
    DATASET_geographic_level = "DATASET_geographic_level"
    DATASET_provenance = "DATASET_provenance"
    DATASET_number_of_dataset_series = "DATASET_number_of_dataset_series"
    DATASET_number_of_structural_data_files = "DATASET_number_of_structural_data_files"
    DATASET_date_of_completion = "DATASET_date_of_completion"
    DATASET_name_and_email_of_individual_completing_this_template = (
        "DATASET_name_and_email_of_individual_completing_this_template"
    )
    DATASET_security_classification = "DATASET_security_classification"
    DATASET_dataset_resource_type = "DATASET_dataset_resource_type"
    DATASET_number_of_non_structural_reference_files = (
        "DATASET_number_of_non_structural_reference_files"
    )
    DATASET_number_of_code_list_files = "DATASET_number_of_code_list_files"
    SERIES_dataset_series_name = "SERIES_dataset_series_name"
    SERIES_google_cloud_platform_bigquery_table_name = (
        "SERIES_google_cloud_platform_bigquery_table_name"
    )
    SERIES_description = "SERIES_description"
    SERIES_reference_period = "SERIES_reference_period"
    SERIES_geographic_coverage = "SERIES_geographic_coverage"
    SERIES_frequency = "SERIES_frequency"
    SERIES_supply_type = "SERIES_supply_type"
    SERIES_wave_number_time_period_covered_survey_only = (
        "SERIES_wave_number_time_period_covered_survey_only"
    )
    SERIES_links_to_online_documentation_and_other_useful_materials = (
        "SERIES_links_to_online_documentation_and_other_useful_materials"
    )
    FILE_google_cloud_platform_bigquery_table_name = (
        "FILE_google_cloud_platform_bigquery_table_name"
    )
    FILE_file_path_and_name = "FILE_file_path_and_name"
    FILE_file_format = "FILE_file_format"
    FILE_column_seperator = "FILE_column_seperator"
    FILE_string_identifier = "FILE_string_identifier"
    FILE_file_description = "FILE_file_description"
    FILE_reference_period = "FILE_reference_period"
    FILE_file_size = "FILE_file_size"
    FILE_file_size_unit = "FILE_file_size_unit"
    FILE_is_code_list = "FILE_is_code_list"
    FILE_number_of_records = "FILE_number_of_records"
    FILE_is_this_file_one_of_a_sequence_to_be_appended_back_together = (
        "FILE_is_this_file_one_of_a_sequence_to_be_appended_back_together"
    )
    FILE_number_of_header_rows = "FILE_number_of_header_rows"
    FILE_number_of_footer_rows = "FILE_number_of_footer_rows"
    FILE_character_encoding = "FILE_character_encoding"
    FILE_hash_value_for_checksum = "FILE_hash_value_for_checksum"
    FILE_notes = "FILE_notes"
    VARS_google_cloud_platform_bigquery_table_name = (
        "VARS_google_cloud_platform_bigquery_table_name"
    )
    VARS_variable_name = "VARS_variable_name"
    VARS_google_cloud_platform_compatible_variable_name = (
        "VARS_google_cloud_platform_compatible_variable_name"
    )
    VARS_variable_label = "VARS_variable_label"
    VARS_variable_description = "VARS_variable_description"
    VARS_position_in_file = "VARS_position_in_file"
    VARS_personally_identifiable_information = (
        "VARS_personally_identifiable_information"
    )
    VARS_variable_data_type = "VARS_variable_data_type"
    VARS_gcp_data_type = "VARS_gcp_data_type"
    VARS_variable_length_precision = "VARS_variable_length_precision"
    VARS_variable_format = "VARS_variable_format"
    VARS_is_primary_key = "VARS_is_primary_key"
    VARS_is_foreign_key = "VARS_is_foreign_key"
    VARS_foreign_key_file_name = "VARS_foreign_key_file_name"
    VARS_foreign_key_variable_name = "VARS_foreign_key_variable_name"
    VARS_nullability = "VARS_nullability"
    VARS_null_values_denoted_by = "VARS_null_values_denoted_by"
    VARS_variable_constraints = "VARS_variable_constraints"
    VARS_applicable_business_rules = "VARS_applicable_business_rules"
    VARS_is_this_a_code = "VARS_is_this_a_code"
    VARS_notes = "VARS_notes"
    CODES_google_cloud_platform_bigquery_table_name = (
        "CODES_google_cloud_platform_bigquery_table_name"
    )
    CODES_variable_name = "CODES_variable_name"
    CODES_key = "CODES_key"
    CODES_value = "CODES_value"
    CODES_notes = "CODES_notes"
    DATASET_ids_business_catalogue_identifier = (
        "DATASET_ids_business_catalogue_identifier"
    )
    DATASET_description = "DATASET_description"
    DATASET_abstract = "DATASET_abstract"
    DATASET_google_cloud_platform_project_name = (
        "DATASET_google_cloud_platform_project_name"
    )
    DATASET_google_cloud_platform_big_query_dataset_name = (
        "DATASET_google_cloud_platform_big_query_dataset_name"
    )
    DATASET_other_unique_identifier_s_for_dataset_resource = (
        "DATASET_other_unique_identifier_s_for_dataset_resource"
    )
    DATASET_frequency = "DATASET_frequency"
    DATASET_geographic_coverage = "DATASET_geographic_coverage"
    DATASET_temporal_coverage = "DATASET_temporal_coverage"
    DATASET_sensitivity_status_for_dataset_resource = (
        "DATASET_sensitivity_status_for_dataset_resource"
    )
    DATASET_sensitivity_tool_url = "DATASET_sensitivity_tool_url"
    DATASET_retention_date = "DATASET_retention_date"
    DATASET_provider_statement_for_retention_removal_or_deletion = (
        "DATASET_provider_statement_for_retention_removal_or_deletion"
    )
    DATASET_removal_date = "DATASET_removal_date"
    DATASET_removal_comments = "DATASET_removal_comments"
    DATASET_data_controller = "DATASET_data_controller"
    DATASET_data_processor = "DATASET_data_processor"
    DATASET_dataset_domain = "DATASET_dataset_domain"
    DATASET_legal_gateway = "DATASET_legal_gateway"
    DATASET_other_legal_gateway = "DATASET_other_legal_gateway"
    DATASET_licensing_status = "DATASET_licensing_status"
    DATASET_metadata_access = "DATASET_metadata_access"
    DATASET_documentation = "DATASET_documentation"
    DATASET_what_are_the_linkage_requirements_for_the_data_within_the_project_scope = "DATASET_what_are_the_linkage_requirements_for_the_data_within_the_project_scope"
    DATASET_how_has_deidentification_been_achieved = (
        "DATASET_how_has_deidentification_been_achieved"
    )
    DATASET_should_this_dataset_be_visible_for_internal_or_external_users = (
        "DATASET_should_this_dataset_be_visible_for_internal_or_external_users"
    )
    DATASET_restrictions_for_access = "DATASET_restrictions_for_access"
    DATASET_research_outputs = "DATASET_research_outputs"
    DATASET_project_approval = "DATASET_project_approval"
    DATASET_disclosure_control = "DATASET_disclosure_control"
    DATASET_research_disclaimer = "DATASET_research_disclaimer"

    # fields added in v3
    VARS_variable_availability = "VARS_variable_availability"
    VARS_row_level_restrictions = "VARS_row_level_restrictions"
    VARS_key_data_type = "VARS_key_data_type"
    VARS_value_data_type = "VARS_value_data_type"
    DATASET_frequency_of_collection = "DATASET_frequency_of_collection"
    DATASET_safe_settings = "DATASET_safe_settings"
    DATASET_access_level = "DATASET_access_level"
    DATASET_subject_to_low_level_access_control = (
        "DATASET_subject_to_low_level_access_control"
    )


# Trailing space in "Full " is present in the dropdown in the excel template
class SupplyType(Enum):
    FULL = "Full "
    APPEND = "Append"


# UPDATE_WITH_VERSION
# 2 = metadata V2
# pandas index terms
TAB_DETAILS: Dict[Union[int, float], Dict[str, TabDetails]] = {
    1: {
        SheetMapper.SERIES.value: TabDetails(label_row=1, data_row=7),
        SheetMapper.FILE.value: TabDetails(label_row=0, data_row=22),
        SheetMapper.VARS.value: TabDetails(label_row=0, data_row=21),
        SheetMapper.CODES.value: TabDetails(label_row=0, data_row=16),
    },
    2: {
        SheetMapper.SERIES.value: TabDetails(label_row=6, data_row=10),
        SheetMapper.FILE.value: TabDetails(label_row=6, data_row=10),
        SheetMapper.VARS.value: TabDetails(label_row=5, data_row=9),
        SheetMapper.CODES.value: TabDetails(label_row=4, data_row=7),
    },
}

EMPTY_VALUES = ["", "None", None, np.nan, "nan", "NULL"]


DATA_TYPES = [
    "ARRAY",
    "ARRAYTYPE",
    "BIGINT",
    "BOOLEAN",
    "BOOLEANTYPE",
    "BYTETYPE",
    "CLOB",
    "DATE",
    "DATETIME",
    "DATETYPE",
    "DECIMAL",
    "DECIMALTYPE",
    "DOUBLE",
    "DOUBLETYPE",
    "FLOAT",
    "FLOATTYPE",
    "INT",
    "INT16",
    "INT32",
    "INT64",
    "INT8",
    "INTEGER",
    "INTEGERTYPE",
    "LONG",
    "LONGTEXT",
    "LONGTYPE",
    "MAP",
    "MAPTYPE",
    "SHORTTEXT",
    "SHORTTYPE",
    "SMALLINT",
    "STR",
    "STRING",
    "STRINGTYPE",
    "STRUCT",
    "STRUCTTYPE",
    "TEXT",
    "TIME",
    "TIMESTAMP",
    "TIMESTAMPTYPE",
    "TINYINT",
    "UNICODESTRING",
]


NON_BREAKING_MANDATORY = [
    MetaMapper.DATASET_acronym.value,
    MetaMapper.DATASET_significant_changes.value,
    MetaMapper.DATASET_data_contributor_s.value,
    MetaMapper.DATASET_purpose_of_this_dataset_resource.value,
    MetaMapper.DATASET_provenance.value,
    MetaMapper.DATASET_date_of_completion.value,
    MetaMapper.DATASET_name_and_email_of_individual_completing_this_template.value,
    MetaMapper.DATASET_number_of_non_structural_reference_files.value,
    MetaMapper.DATASET_number_of_code_list_files.value,
    MetaMapper.SERIES_wave_number_time_period_covered_survey_only.value,
    MetaMapper.SERIES_links_to_online_documentation_and_other_useful_materials.value,
    MetaMapper.FILE_column_seperator.value,
    MetaMapper.FILE_string_identifier.value,
    MetaMapper.FILE_file_description.value,
    MetaMapper.FILE_reference_period.value,
    MetaMapper.FILE_file_size.value,
    MetaMapper.FILE_file_size_unit.value,
    MetaMapper.FILE_is_code_list.value,
    MetaMapper.FILE_number_of_records.value,
    MetaMapper.FILE_is_this_file_one_of_a_sequence_to_be_appended_back_together.value,
    # MetaMapper.FILE_number_of_footer_rows.value,
    MetaMapper.FILE_character_encoding.value,
    MetaMapper.FILE_hash_value_for_checksum.value,
    MetaMapper.FILE_notes.value,
    MetaMapper.VARS_google_cloud_platform_compatible_variable_name.value,
    MetaMapper.VARS_variable_label.value,
    # MetaMapper.VARS_variable_description.value,
    MetaMapper.VARS_position_in_file.value,
    # MetaMapper.VARS_personally_identifiable_information.value,
    MetaMapper.VARS_gcp_data_type.value,
    MetaMapper.VARS_variable_length_precision.value,
    MetaMapper.VARS_variable_format.value,
    # MetaMapper.VARS_is_primary_key.value,
    # MetaMapper.VARS_is_foreign_key.value,
    MetaMapper.VARS_foreign_key_file_name.value,
    MetaMapper.VARS_foreign_key_variable_name.value,
    MetaMapper.VARS_null_values_denoted_by.value,
    MetaMapper.VARS_variable_constraints.value,
    MetaMapper.VARS_applicable_business_rules.value,
    MetaMapper.VARS_is_this_a_code.value,
    MetaMapper.VARS_notes.value,
    MetaMapper.CODES_google_cloud_platform_bigquery_table_name.value,
    MetaMapper.CODES_variable_name.value,
    MetaMapper.CODES_key.value,
    MetaMapper.CODES_value.value,
    MetaMapper.CODES_notes.value,
    MetaMapper.DATASET_google_cloud_platform_project_name.value,
    # MetaMapper.DATASET_other_unique_identifier_s_for_dataset_resource.value,
    MetaMapper.DATASET_sensitivity_tool_url.value,
    MetaMapper.DATASET_provider_statement_for_retention_removal_or_deletion.value,
    MetaMapper.DATASET_removal_date.value,
    MetaMapper.DATASET_removal_comments.value,
    MetaMapper.DATASET_data_processor.value,
    MetaMapper.DATASET_dataset_domain.value,
    MetaMapper.DATASET_other_legal_gateway.value,
    MetaMapper.DATASET_documentation.value,
    MetaMapper.DATASET_what_are_the_linkage_requirements_for_the_data_within_the_project_scope.value,
    # MetaMapper.DATASET_how_has_deidentification_been_achieved.value,
    MetaMapper.DATASET_frequency_of_collection.value,
]
