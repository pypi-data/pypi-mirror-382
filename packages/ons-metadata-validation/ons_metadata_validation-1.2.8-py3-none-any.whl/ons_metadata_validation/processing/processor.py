import itertools
import re
import warnings
from collections import defaultdict
from copy import deepcopy
from typing import Dict

import attrs
import pandas as pd
from attrs.validators import instance_of, optional
from tqdm import tqdm

import ons_metadata_validation.ids_common_utils.cleaning as ids_c
import ons_metadata_validation.processing.utils as utils
from ons_metadata_validation.fixing.fixing_utils import apply_fixes
from ons_metadata_validation.ids_common_utils.build_spark_schema import (
    get_schemas_for_series,
)
from ons_metadata_validation.processing.validate_funcs import (
    validate_comparative_checks,
    validate_rowwise_comparative_checks,
    validate_xl_single_values,
)
from ons_metadata_validation.reference.constants import MetaMapper, SheetMapper
from ons_metadata_validation.reference.role_configs import ROLE_SKIP_KEYS
from ons_metadata_validation.validation.comparative_validations import (
    COMPARATIVE_VALIDATIONS,
)
from ons_metadata_validation.validation.rowwise_validations import (
    ROWWISE_VALIDATIONS,
)
from ons_metadata_validation.validation.validations import (
    SINGLE_VALUE_VALIDATIONS,
)


@attrs.define
class MetadataProcessor:
    md_filepath: str = attrs.field(validator=[instance_of(str)])
    variable_check_set: str = attrs.field(validator=[instance_of(str)])
    make_report: bool = attrs.field(validator=[instance_of(bool)])
    save_report: bool = attrs.field(validator=[instance_of(bool)])
    save_corrected_copy: bool = attrs.field(validator=[instance_of(bool)])
    xl: dict = attrs.field(validator=[instance_of(dict)], init=False)
    target_version: str = attrs.field(validator=[instance_of(str)], init=False)
    template_map: dict = attrs.field(validator=[instance_of(dict)], init=False)
    tab_lens: dict = attrs.field(validator=[instance_of(dict)], init=False)
    fails_df: pd.DataFrame = attrs.field(
        validator=[instance_of(pd.DataFrame)], init=False
    )
    applied_fixes_df: pd.DataFrame = attrs.field(
        validator=[instance_of(pd.DataFrame)], init=False
    )
    tab_details: dict = attrs.field(validator=[instance_of(dict)], init=False)
    recorded_validation_checks: dict = attrs.field(
        validator=[instance_of(dict)], init=False
    )
    tabs_to_validate: list = attrs.field(
        default=None, validator=[optional(instance_of(list))]
    )
    json: dict = attrs.field(validator=[instance_of(dict)], init=False)
    schemas: dict = attrs.field(validator=[instance_of(dict)], init=False)
    modified_variables_json: dict = attrs.field(
        validator=[instance_of(dict)], init=False
    )
    nested_errors: dict = attrs.field(validator=[instance_of(dict)], init=False)

    def __attrs_post_init__(self):
        # suppresses warning for inconsequential data validation extension
        warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
        if self.tabs_to_validate is None:
            self.tabs_to_validate = [
                SheetMapper.RESOURCE.value,
                SheetMapper.SERIES.value,
                SheetMapper.FILE.value,
                SheetMapper.VARS.value,
                SheetMapper.CODES.value,
                SheetMapper.BACK_OFFICE.value,
            ]

    def run(self) -> None:
        """main method to run MetadataProcessor."""
        self.load_xl()

        if float(re.sub(r"[A-Za-z _]", "", self.target_version)) == 1:
            raise ValueError(
                f"Validating template version {self.target_version} is not supported. "
                "Please convert to V2 or above using `convert_template_to_version` before validating"
            )

        self.validate_xl()
        self.record_validation_checks()

        if float(re.sub(r"[A-Za-z _]", "", self.target_version)) >= 3:
            self.write_to_json()
            self.schemas, self.modified_variables_json, self.nested_errors = (
                get_schemas_for_series(self.json, self.target_version)
            )
            self.add_nested_errors_to_fails_df()

    def load_xl(self) -> None:
        """
        Load the xl to a list of dicts, preprocess the data and record the
        lengths of each of the tabs.
        This also renames the columns to our internal reference field names.
        """
        self.xl = pd.read_excel(
            self.md_filepath,
            sheet_name=None,
            header=None,
            engine="openpyxl",
            keep_default_na=False,
        )
        # this is the only time we have to hard-code a sheet name
        # there may be a time where the "h" is capitalised and this will fail
        # ...but it is not this day
        self.target_version = str(
            self.xl["Change history"].iloc[utils.xl_cell_ref_to_pd_index("D1")]
        )
        self.template_map, self.tab_details = utils.get_template_map(
            self.target_version
        )
        utils.validate_metadata_structure(self.template_map, self.xl)
        rename_maps = utils.create_tab_maps(self.template_map)
        self.xl = self.preprocess_xl(rename_maps)
        self.tab_lens = self.get_tab_lens()
        if self.save_corrected_copy:
            self.xl, self.applied_fixes_df = apply_fixes(
                self.xl, SINGLE_VALUE_VALIDATIONS
            )

    def preprocess_xl(
        self,
        rename_maps: Dict[str, Dict[str, str]],
    ) -> Dict[str, pd.DataFrame]:
        """Remove all unnecessary fields and only retain the ones we need to validate.

        Args:
            rename_maps (Dict[str, Dict[str, str]]): the mapping to rename each of the
                columns to our internal references.

        Returns:
            Dict[str, pd.DataFrame]: DataFrame per tab.
        """

        for tab in tqdm(self.tab_details, "preprocessing xl"):
            self.xl[tab].columns = self.xl[tab].iloc[self.tab_details[tab].label_row]
            self.xl[tab] = self.xl[tab].iloc[self.tab_details[tab].data_row :]
            self.xl[tab] = self.xl[tab].rename(columns=rename_maps[tab])[
                list(rename_maps[tab].values())
            ]
            self.xl[tab] = ids_c.trim_whitespace_rows(self.xl[tab])

        resource_data = defaultdict(dict)

        for v in self.template_map.values():
            if v is None:
                continue
            tab = v["tab"]
            if tab in [
                SheetMapper.RESOURCE.value,
                SheetMapper.BACK_OFFICE.value,
            ]:
                resource_data[tab][v["std_name"]] = self.xl[tab].iloc[
                    utils.xl_cell_ref_to_pd_index(v["value_cell"])
                ]

        for tab in [SheetMapper.RESOURCE.value, SheetMapper.BACK_OFFICE.value]:
            self.xl[tab] = pd.DataFrame(resource_data[tab], index=[0])

        return self.xl

    def get_tab_lens(self) -> Dict[str, int]:
        """Get the length of each of the tabs.

        Returns:
            Dict[str, int]: tab name: tab length.
        """
        tabs = [
            SheetMapper.SERIES.value,
            SheetMapper.FILE.value,
            SheetMapper.VARS.value,
            SheetMapper.CODES.value,
        ]
        return {tab: len(self.xl[tab]) for tab in tabs}

    def validate_xl(self) -> pd.DataFrame:
        """Wrapper method that runs each type of validation we have.

        Returns:
            pd.DataFrame: fails_df with 1 record per fail.
        """
        single_value_fails = validate_xl_single_values(
            self.xl,
            self.template_map,
            SINGLE_VALUE_VALIDATIONS,
            ROLE_SKIP_KEYS[self.variable_check_set],
            tabs_to_validate=self.tabs_to_validate,
        )
        rowwise_fails = validate_rowwise_comparative_checks(
            self.xl, self.template_map, ROWWISE_VALIDATIONS
        )
        comparative_checks = validate_comparative_checks(
            self.xl, self.template_map, COMPARATIVE_VALIDATIONS
        )
        self.fails_df = pd.concat(
            [single_value_fails, rowwise_fails, comparative_checks]
        )
        return self.fails_df

    def record_validation_checks(self) -> None:
        """Record each of the checks that has been run on the template."""
        recorded_validation_checks = []

        for v in self.template_map.values():
            if v is None:
                continue
            field_validations = SINGLE_VALUE_VALIDATIONS[v["std_name"]]
            recorded_validation_checks.append(
                {
                    "tab": v["tab"],
                    "name": v["name"],
                    "enum": bool(v["enum"]),
                    "hard_checks": ", ".join(
                        [f.__name__ for f in field_validations.get("hard", [])]
                    ),
                    "soft_checks": ", ".join(
                        [f.__name__ for f in field_validations.get("soft", [])]
                    ),
                }
            )

        rowwise_validations = [
            {
                "tab": validation[0],
                "names": ", ".join(
                    [self.template_map[col]["name"] for col in validation[1]]
                ),
                "check": validation[2].__name__,
                "level": validation[3],
            }
            for validation in ROWWISE_VALIDATIONS
        ]

        comparative_validations = [
            {
                "names": ", ".join(
                    [self.template_map[col]["name"] for col in validation[0]]
                ),
                "check": validation[1].__name__,
                "level": validation[2],
            }
            for validation in COMPARATIVE_VALIDATIONS
        ]

        self.recorded_validation_checks = {
            "single_validation_checks": pd.DataFrame(recorded_validation_checks),
            "rowwise_validations": pd.DataFrame(rowwise_validations),
            "comparative_validations": pd.DataFrame(comparative_validations),
        }
        if self.save_corrected_copy:
            self.recorded_validation_checks["applied_fixes"] = self.applied_fixes_df

    def get_clean_json_xl_copy(self) -> Dict[str, pd.DataFrame]:
        """Basic cleaning to the xl to get it ready to be a json.

        Returns:
            Dict[str, pd.DataFrame]: the cleaned xl.
        """
        xl = deepcopy(self.xl)

        cleaning_transformations = [
            (
                SheetMapper.VARS.value,
                MetaMapper.VARS_nullability.value,
                utils.is_nullable,
                {},
            ),
        ]
        for sheet, col, func, kwargs in cleaning_transformations:
            xl[sheet][col] = xl[sheet][col].apply(func, **kwargs)
        return xl

    def write_to_json(self):
        """Transform the xl to json."""
        json_xl = self.get_clean_json_xl_copy()

        tabs_cols = [
            (
                SheetMapper.SERIES.value,
                MetaMapper.SERIES_google_cloud_platform_bigquery_table_name.value,
            ),
            (
                SheetMapper.FILE.value,
                MetaMapper.FILE_google_cloud_platform_bigquery_table_name.value,
            ),
            (
                SheetMapper.VARS.value,
                MetaMapper.VARS_google_cloud_platform_bigquery_table_name.value,
            ),
        ]
        tabs_by_series = {
            tab: utils.collapse_df(json_xl[tab], col) for tab, col in tabs_cols
        }

        resource = self.xl[SheetMapper.RESOURCE.value].to_dict("index")[0]
        back_office = self.xl[SheetMapper.BACK_OFFICE.value].to_dict("index")[0]
        self.json = {**resource, **back_office}
        # assume no duplicate series
        # if there are duplicates the second value will overwrite the first value
        self.json[SheetMapper.SERIES.value] = {
            k: v[0] for k, v in tabs_by_series[SheetMapper.SERIES.value].items()
        }

        for series in self.json[SheetMapper.SERIES.value].keys():
            # in case there are series on one tab and not others
            # we pick it up elsewhere and print an issue
            # not worth raising another error here
            try:
                self.json[SheetMapper.SERIES.value][series][SheetMapper.FILE.value] = (
                    utils.records_to_json(
                        tabs_by_series[SheetMapper.FILE.value][series],
                        MetaMapper.FILE_file_path_and_name.value,
                    )
                )
            except KeyError:
                print(
                    f"'{series}' not present in '{SheetMapper.FILE.value}'. Not able to add to JSON."
                )

            try:
                self.json[SheetMapper.SERIES.value][series][SheetMapper.VARS.value] = (
                    utils.records_to_json(
                        tabs_by_series[SheetMapper.VARS.value][series],
                        MetaMapper.VARS_variable_name.value,
                    )
                )
            except KeyError:
                print(
                    f"'{series}' not present in '{SheetMapper.VARS.value}'. Not able to add to JSON."
                )

    def add_nested_errors_to_fails_df(self):
        all_nested_fails = list(
            itertools.chain.from_iterable(self.nested_errors.values())
        )
        nested_fails_df = pd.DataFrame([attrs.asdict(e) for e in all_nested_fails])
        self.fails_df = pd.concat([self.fails_df, nested_fails_df])
