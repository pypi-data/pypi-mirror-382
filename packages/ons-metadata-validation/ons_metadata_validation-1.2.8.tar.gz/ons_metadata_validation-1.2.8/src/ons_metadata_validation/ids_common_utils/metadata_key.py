from enum import Enum

from ons_metadata_validation.reference.constants import MetaMapper


class MetadataKey(Enum):
    """Metadata JSON key constants."""

    BQ_DATASET = "bq_dataset"
    DATASET_VISIBILITY = "dataset_visibility"
    DATASET_ABSTRACT = "dataset_abstract"
    DATASET_ACCESS_LEVELS = "dataset_access_levels"
    DATASET_ALTLABEL = "dataset_altlabel"
    DATASET_COMPLETION_CONTACT = "dataset_completion_contact"
    DATASET_COMPLETION_DATE = "dataset_completion_date"
    DATASET_CONTRIBUTOR = "dataset_contributor"
    DATASET_CONTROLLER = "dataset_controller"
    DATASET_DEIDENTIFICATION_METHOD = "dataset_deidentification"
    DATASET_DESCRIPTION = "dataset_description"
    DATASET_DISC_CONTROL = "dataset_disc_control"
    DATASET_FREQUENCY = "dataset_frequency"
    DATASET_FREQUENCY_OF_DELIVERY = "dataset_frequency_of_delivery"
    DATASET_GEOGRAPHICAL_COVERAGE = "dataset_geographical_coverage"
    DATASET_IDENTIFIER = "dataset_identifier"
    DATASET_KEYWORD = "dataset_keyword"
    DATASET_LEGAL_GATEWAY = "dataset_legal_gateway"
    DATASET_LICENSE = "dataset_license"
    DATASET_LINKAGE_REQUIREMENTS = "dataset_linkage_requirements"
    DATASET_LLAC = "dataset_llac"
    DATASET_METADATA_ACCESS = "dataset_metadata_access"
    DATASET_N_CODE_LISTS = "dataset_n_code_lists"
    DATASET_N_DATA_FILES = "dataset_n_data_files"
    DATASET_N_REFERENCE_FILES = "dataset_n_reference_files"
    DATASET_NUMBER = "dataset_number"
    DATASET_ALT_IDENTIFIER = "dataset_alt_identifier"
    DATASET_OTHER_LEGAL_GATEWAY = "dataset_other_legal_gateway"
    DATASET_OUTPUTS = "dataset_outputs"
    DATASET_PROCESSOR = "dataset_processor"
    DATASET_PROJ_APPROVAL = "dataset_proj_approval"
    DATASET_PROJECT_NAME = "dataset_project_name"
    DATASET_PROVENANCE = "dataset_provenance"
    DATASET_PUBLISHER = "dataset_publisher"
    DATASET_PURPOSE = "dataset_purpose"
    DATASET_REFERENCES = "dataset_references"
    DATASET_REMOVAL_COMMENT = "dataset_removal_comment"
    DATASET_REMOVAL_DATE = "dataset_removal_date"
    DATASET_RESEARCH_DISC = "dataset_research_disc"
    DATASET_RESTRICTIONS = "dataset_restrictions"
    DATASET_RETENTION_DATE = "dataset_retention_date"
    DATASET_SAFE_SETTINGS = "dataset_safe_settings"
    DATASET_SECURITY_CLASSIFICATION = "dataset_security_classification"
    DATASET_SENSITIVITY = "dataset_sensitivity"
    DATASET_SENSITIVITY_URL = "dataset_sensitivity_url"
    DATASET_SPATIAL_GRANULARITY = "dataset_spatial_granularity"
    DATASET_STATUS = "dataset_status"
    DATASET_TEMPORAL_COVERAGE = "dataset_temporal_coverage"
    DATASET_THEME = "dataset_theme"
    DATASET_TITLE = "dataset_title"
    DATASET_TYPE = "dataset_type"
    METADATA_PARSER_VERSION = "metadata_parser_version"
    SIGNIFICANT_CHANGES = "significant_changes"
    DATA_SERIES = "data_series"
    COLUMNS = "columns"
    DATA_SERIES_TYPE = "data_series_type"
    ENCODING = "encoding"
    FILES_METADATA = "files_metadata"
    HEADERS = "headers"
    SERIES_NAME = "series_name"
    SERIES_FREQUENCY = "series_frequency"
    SERIES_REFERENCE_PERIOD = "series_reference_period"
    SUPPLY_TYPE = "supply_type"
    COLUMN_SEPERATOR = "column_seperator"
    FILE_CHARACTER_ENCODING = "file_character_encoding"
    FILE_CHECKSUM = "file_checksum"
    FILE_FORMAT = "file_format"
    FILE_IS_CODE_LIST = "file_is_code_list"
    FILE_NUMBER_FOOTER_RECORDS = "file_number_footer_records"
    FILE_NUMBER_HEADER_RECORDS = "file_number_header_records"
    FILE_NUMBER_RECORDS = "file_number_records"
    FILE_PATH = "file_path"
    FILE_SERIES_NAME = "file_series_name"
    FILE_SIZE = "file_size"
    FILE_SIZE_UNIT = "file_size_unit"
    FILE_TEXT_QUALIFIER = "file_text_qualifier"
    COLUMN_SERIES_NAME = "column_series_name"
    COLUMN_NAME = "column_name"
    COLUMN_DATA_TYPE = "column_data_type"
    COLUMN_DESCRIPTION = "column_description"
    COLUMN_FORMAT = "column_format"
    COLUMN_IS_FK = "column_is_fk"
    COLUMN_IS_PII = "column_is_pii"
    COLUMN_IS_PK = "column_is_pk"
    COLUMN_LENGTH = "column_length"
    COLUMN_NULL_VALUE = "column_null_value"
    COLUMN_NULLABLE = "column_nullable"
    COLUMN_PRECISION = "column_precision"
    COLUMN_SCALE = "column_scale"
    MAP_KEY_DATA_TYPE = "map_key_data_type"
    MAP_VALUE_DATA_TYPE = "map_value_data_type"
    VARIABLE_AVAILABILITY = "variable_availability"
    VARIABLE_FILTER = "variable_filter"


METADATAKEY_METAMAPPER_LOOKUP = {
    MetadataKey.DATASET_TITLE.value: MetaMapper.DATASET_dataset_resource_name.value,
    MetadataKey.DATASET_ALTLABEL.value: MetaMapper.DATASET_acronym.value,
    MetadataKey.DATASET_PUBLISHER.value: MetaMapper.DATASET_data_creator.value,
    MetadataKey.DATASET_CONTRIBUTOR.value: MetaMapper.DATASET_data_contributor_s.value,
    MetadataKey.DATASET_PURPOSE.value: MetaMapper.DATASET_purpose_of_this_dataset_resource.value,
    MetadataKey.DATASET_KEYWORD.value: MetaMapper.DATASET_search_keywords.value,
    MetadataKey.DATASET_THEME.value: MetaMapper.DATASET_dataset_theme.value,
    MetadataKey.DATASET_SPATIAL_GRANULARITY.value: MetaMapper.DATASET_geographic_level.value,
    MetadataKey.DATASET_PROVENANCE.value: MetaMapper.DATASET_provenance.value,
    MetadataKey.DATASET_NUMBER.value: MetaMapper.DATASET_number_of_dataset_series.value,
    MetadataKey.DATASET_N_DATA_FILES.value: MetaMapper.DATASET_number_of_structural_data_files.value,
    MetadataKey.DATASET_COMPLETION_DATE.value: MetaMapper.DATASET_date_of_completion.value,
    MetadataKey.DATASET_COMPLETION_CONTACT.value: MetaMapper.DATASET_name_and_email_of_individual_completing_this_template.value,
    MetadataKey.DATASET_SECURITY_CLASSIFICATION.value: MetaMapper.DATASET_security_classification.value,
    MetadataKey.DATASET_TYPE.value: MetaMapper.DATASET_dataset_resource_type.value,
    MetadataKey.DATASET_N_REFERENCE_FILES.value: MetaMapper.DATASET_number_of_non_structural_reference_files.value,
    MetadataKey.DATASET_N_CODE_LISTS.value: MetaMapper.DATASET_number_of_code_list_files.value,
    "series_friendly_name": MetaMapper.SERIES_dataset_series_name.value,
    MetadataKey.SERIES_NAME.value: MetaMapper.SERIES_google_cloud_platform_bigquery_table_name.value,
    "series_description": MetaMapper.SERIES_description.value,
    MetadataKey.SERIES_REFERENCE_PERIOD.value: MetaMapper.SERIES_reference_period.value,
    MetadataKey.SUPPLY_TYPE.value: MetaMapper.SERIES_supply_type.value,
    MetadataKey.SERIES_FREQUENCY.value: MetaMapper.SERIES_frequency.value,
    "column_seperator": MetaMapper.FILE_column_seperator.value,
    MetadataKey.FILE_SERIES_NAME.value: MetaMapper.FILE_google_cloud_platform_bigquery_table_name.value,
    MetadataKey.FILE_PATH.value: MetaMapper.FILE_file_path_and_name.value,
    MetadataKey.FILE_FORMAT.value: MetaMapper.FILE_file_format.value,
    MetadataKey.FILE_TEXT_QUALIFIER.value: MetaMapper.FILE_string_identifier.value,
    MetadataKey.FILE_SIZE.value: MetaMapper.FILE_file_size.value,
    MetadataKey.FILE_SIZE_UNIT.value: MetaMapper.FILE_file_size_unit.value,
    MetadataKey.FILE_IS_CODE_LIST.value: MetaMapper.FILE_is_code_list.value,
    MetadataKey.FILE_NUMBER_RECORDS.value: MetaMapper.FILE_number_of_records.value,
    MetadataKey.FILE_NUMBER_HEADER_RECORDS.value: MetaMapper.FILE_number_of_header_rows.value,
    MetadataKey.FILE_NUMBER_FOOTER_RECORDS.value: MetaMapper.FILE_number_of_footer_rows.value,
    MetadataKey.FILE_CHARACTER_ENCODING.value: MetaMapper.FILE_character_encoding.value,
    MetadataKey.FILE_CHECKSUM.value: MetaMapper.FILE_hash_value_for_checksum.value,
    MetadataKey.COLUMN_SERIES_NAME.value: MetaMapper.VARS_google_cloud_platform_bigquery_table_name.value,
    MetadataKey.COLUMN_NAME.value: MetaMapper.VARS_variable_name.value,
    MetadataKey.COLUMN_DESCRIPTION.value: MetaMapper.VARS_variable_description.value,
    MetadataKey.COLUMN_IS_PII.value: MetaMapper.VARS_personally_identifiable_information.value,
    MetadataKey.COLUMN_DATA_TYPE.value: MetaMapper.VARS_variable_data_type.value,
    MetadataKey.COLUMN_LENGTH.value: MetaMapper.VARS_variable_length_precision.value,
    MetadataKey.COLUMN_FORMAT.value: MetaMapper.VARS_variable_format.value,
    MetadataKey.COLUMN_IS_PK.value: MetaMapper.VARS_is_primary_key.value,
    MetadataKey.COLUMN_IS_FK.value: MetaMapper.VARS_is_foreign_key.value,
    MetadataKey.COLUMN_NULLABLE.value: MetaMapper.VARS_nullability.value,
    MetadataKey.COLUMN_NULL_VALUE.value: MetaMapper.VARS_null_values_denoted_by.value,
    MetadataKey.DATASET_IDENTIFIER.value: MetaMapper.DATASET_ids_business_catalogue_identifier.value,
    MetadataKey.DATASET_DESCRIPTION.value: MetaMapper.DATASET_description.value,
    MetadataKey.DATASET_ABSTRACT.value: MetaMapper.DATASET_abstract.value,
    MetadataKey.DATASET_PROJECT_NAME.value: MetaMapper.DATASET_google_cloud_platform_project_name.value,
    MetadataKey.BQ_DATASET.value: MetaMapper.DATASET_google_cloud_platform_big_query_dataset_name.value,
    MetadataKey.DATASET_ALT_IDENTIFIER.value: MetaMapper.DATASET_other_unique_identifier_s_for_dataset_resource.value,
    MetadataKey.DATASET_FREQUENCY.value: MetaMapper.DATASET_frequency.value,
    MetadataKey.DATASET_GEOGRAPHICAL_COVERAGE.value: MetaMapper.DATASET_geographic_coverage.value,
    MetadataKey.DATASET_TEMPORAL_COVERAGE.value: MetaMapper.DATASET_temporal_coverage.value,
    MetadataKey.DATASET_SENSITIVITY.value: MetaMapper.DATASET_sensitivity_status_for_dataset_resource.value,
    MetadataKey.DATASET_SENSITIVITY_URL.value: MetaMapper.DATASET_sensitivity_tool_url.value,
    MetadataKey.DATASET_RETENTION_DATE.value: MetaMapper.DATASET_provider_statement_for_retention_removal_or_deletion.value,
    MetadataKey.DATASET_REMOVAL_DATE.value: MetaMapper.DATASET_removal_date.value,
    MetadataKey.DATASET_REMOVAL_COMMENT.value: MetaMapper.DATASET_removal_comments.value,
    MetadataKey.DATASET_CONTROLLER.value: MetaMapper.DATASET_data_controller.value,
    MetadataKey.DATASET_PROCESSOR.value: MetaMapper.DATASET_data_processor.value,
    "dataset_domain": MetaMapper.DATASET_dataset_domain.value,
    MetadataKey.DATASET_LEGAL_GATEWAY.value: MetaMapper.DATASET_legal_gateway.value,
    MetadataKey.DATASET_OTHER_LEGAL_GATEWAY.value: MetaMapper.DATASET_other_legal_gateway.value,
    MetadataKey.DATASET_LICENSE.value: MetaMapper.DATASET_licensing_status.value,
    MetadataKey.DATASET_METADATA_ACCESS.value: MetaMapper.DATASET_metadata_access.value,
    MetadataKey.DATASET_REFERENCES.value: MetaMapper.DATASET_documentation.value,
    MetadataKey.DATASET_LINKAGE_REQUIREMENTS.value: MetaMapper.DATASET_what_are_the_linkage_requirements_for_the_data_within_the_project_scope.value,
    MetadataKey.DATASET_DEIDENTIFICATION_METHOD.value: MetaMapper.DATASET_how_has_deidentification_been_achieved.value,
    MetadataKey.DATASET_VISIBILITY.value: MetaMapper.DATASET_should_this_dataset_be_visible_for_internal_or_external_users.value,
    MetadataKey.DATASET_RESTRICTIONS.value: MetaMapper.DATASET_restrictions_for_access.value,
    MetadataKey.DATASET_OUTPUTS.value: MetaMapper.DATASET_research_outputs.value,
    MetadataKey.DATASET_PROJ_APPROVAL.value: MetaMapper.DATASET_project_approval.value,
    MetadataKey.DATASET_DISC_CONTROL.value: MetaMapper.DATASET_disclosure_control.value,
    MetadataKey.DATASET_RESEARCH_DISC.value: MetaMapper.DATASET_research_disclaimer.value,
    MetadataKey.VARIABLE_AVAILABILITY.value: MetaMapper.VARS_variable_availability.value,
    MetadataKey.VARIABLE_FILTER.value: MetaMapper.VARS_row_level_restrictions.value,
    MetadataKey.DATASET_SAFE_SETTINGS.value: MetaMapper.DATASET_safe_settings.value,
    MetadataKey.DATASET_ACCESS_LEVELS.value: MetaMapper.DATASET_access_level.value,
    MetadataKey.DATASET_LLAC.value: MetaMapper.DATASET_subject_to_low_level_access_control.value,
    MetadataKey.DATASET_FREQUENCY_OF_DELIVERY.value: MetaMapper.DATASET_frequency.value,
}
