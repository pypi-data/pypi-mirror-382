import argparse
from typing import List, Optional

from ons_metadata_validation.outputs.excel_outputs import (
    outputs_main,
)
from ons_metadata_validation.processing.processor import (
    MetadataProcessor,
)
from ons_metadata_validation.utils.logger import setup_logger


def main(
    md_filepath: str,
    variable_check_set: str = "cmar",
    make_report: bool = True,
    save_report: bool = True,
    save_corrected_copy: bool = False,
    save_commented_copy: bool = True,
    destination_folder: Optional[str] = None,
    use_logging: bool = False,
    log_folder: str = "",
    logging_level: str = "debug",
    tabs_to_validate: Optional[List[str]] = None,
):
    if use_logging:
        if log_folder == "":
            raise RuntimeError("log save folder not specified")
        setup_logger(log_folder, logging_level)

    # validate args
    if not any([make_report, save_report, save_corrected_copy, save_commented_copy]):
        raise RuntimeError(
            f"Must have at least one option selected: [make_report, save_report, save_corrected_copy, save_commented_copy] {[make_report, save_report, save_corrected_copy, save_commented_copy]}"
        )

    processor = MetadataProcessor(
        md_filepath,
        variable_check_set=variable_check_set,
        make_report=make_report,
        save_report=save_report,
        save_corrected_copy=save_corrected_copy,
        tabs_to_validate=tabs_to_validate,
    )
    processor.run()
    return outputs_main(
        processor=processor,
        save_folder=destination_folder,
        save_commented_copy=save_commented_copy,
    )


def main_cli() -> None:
    parser = argparse.ArgumentParser(description="validate metadata template")
    parser.add_argument(
        "md_filepath", type=str, help="the filepath to the metdata template"
    )
    parser.add_argument(
        "variable_check_set",
        default="cmar",
        const="cmar",
        nargs="?",
        choices=["cmar", "full"],
        type=str,
        help="the role config to apply",
    )
    parser.add_argument(
        "make_report",
        default=True,
        nargs="?",
        type=bool,
        help="make the dataframes for the validation report",
    )
    parser.add_argument(
        "save_report",
        default=True,
        nargs="?",
        type=bool,
        help="save the validation report",
    )
    parser.add_argument(
        "save_corrected_copy",
        default=False,
        nargs="?",
        type=bool,
        help="create a corrected version of the template",
    )
    parser.add_argument(
        "save_commented_copy",
        default=True,
        nargs="?",
        type=bool,
        help="create a commented version of the template",
    )
    parser.add_argument(
        "destination_folder",
        default=None,
        nargs="?",
        type=str,
        help="save report in directory, defaults to same location as metadata file",
    )
    parser.add_argument(
        "tabs_to_validate",
        default=None,
        nargs="?",
        type=list,
        help="which specific tabs to validate",
    )

    args = parser.parse_args()

    main(
        args.md_filepath,
        args.variable_check_set,
        args.make_report,
        args.save_report,
        args.save_corrected_copy,
        args.save_commented_copy,
        args.destination_folder,
        tabs_to_validate=args.tabs_to_validate,
    )


if __name__ == "__main__":
    main_cli()
