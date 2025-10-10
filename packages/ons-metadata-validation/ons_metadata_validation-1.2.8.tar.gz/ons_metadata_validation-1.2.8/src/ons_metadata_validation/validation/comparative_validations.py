import ons_metadata_validation.validation._comparative_validation_checks as comp_vc
from ons_metadata_validation.reference.constants import MetaMapper

# these apply the validations to each of the values in the keys list
# the keys are stored in the list of this structure
# interface is: (keys, func, fail_type, kwargs)
COMPARATIVE_VALIDATIONS = [
    (
        [
            MetaMapper.SERIES_google_cloud_platform_bigquery_table_name.value,
            MetaMapper.FILE_file_path_and_name.value,
            MetaMapper.FILE_hash_value_for_checksum.value,
        ],
        comp_vc.must_not_have_duplicate_values,
        "hard_comparative",
        {},
    ),
    (
        [
            MetaMapper.SERIES_google_cloud_platform_bigquery_table_name.value,
            MetaMapper.FILE_google_cloud_platform_bigquery_table_name.value,
            MetaMapper.VARS_google_cloud_platform_bigquery_table_name.value,
            MetaMapper.CODES_google_cloud_platform_bigquery_table_name.value,
        ],
        comp_vc.table_names_must_appear_in_main_tabs,
        "hard_comparative",
        {},
    ),
    (
        [MetaMapper.VARS_variable_name.value],
        comp_vc.must_have_unique_values_in_group,
        "hard_comparative",
        {
            "groupby_col": MetaMapper.VARS_google_cloud_platform_bigquery_table_name.value
        },
    ),
    (
        [
            MetaMapper.DATASET_number_of_dataset_series.value,
            MetaMapper.SERIES_google_cloud_platform_bigquery_table_name.value,
        ],
        comp_vc.number_of_dataset_entries_must_match,
        "hard_comparative",
        {},
    ),
    (
        [
            MetaMapper.DATASET_number_of_structural_data_files.value,
            MetaMapper.FILE_google_cloud_platform_bigquery_table_name.value,
        ],
        comp_vc.number_of_dataset_entries_must_match,
        "hard_comparative",
        {},
    ),
    (
        [
            MetaMapper.DATASET_data_creator.value,
            MetaMapper.DATASET_data_contributor_s.value,
        ],
        comp_vc.must_not_match_other_field,
        "soft_comparative",
        {},
    ),
    (
        [
            MetaMapper.SERIES_google_cloud_platform_bigquery_table_name.value,
            MetaMapper.FILE_google_cloud_platform_bigquery_table_name.value,
            MetaMapper.VARS_google_cloud_platform_bigquery_table_name.value,
        ],
        comp_vc.must_have_at_least_one_record,
        "hard_comparative",
        {},
    ),
]
