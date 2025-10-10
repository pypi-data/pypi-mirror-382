# ONS metadata validation tool

*[Looking for guidance on the template v2 to v3 conversion feature? See below...](#version-conversion)*

## Background
This project is for automatically validating metadata templates that accompany IDS data deliveries. The fields in a filled metadata template are each checked against a set of defined conditions. 

For example, many fields are mandatory; many have a maximum number of characters; some fields are not allowed to contain spaces or special characters; and so on.

A metadata template with missing mandatory values or other issues with its format or content will prevent the accompanying dataset from being ingested. This then requires the back-and-forth of resubmission, and causes delays.

## What it does

This tool produces an excel report detailing failed validation checks for a given metadata template. There are also two optional outputs:

* A commented version of the input file, where cells with validation issues are highlighted and a mouseover note names each check that has failed.

* An edited version of the input file, where cells with easily-fixed issues such as missing full stops or trailing whitespace have been automatically updated.

*Note that some metadata requirements cannot be programmatically validated. Some human inspection will always be necessary, for example to sense-check free text fields.*

The tool is designed to work with metadata templates from v2.0 onwards. When pointed at a later version of the template, it should identify the version and update its expectations of the form's format without requiring specific input from the user.

## Documentation

This readme is written for the benefit of end users, such as the CMAR team. It aims to make minimal assumptions about previous experience.

A **recorded demo and tutorial** is available on SharePoint for internal users. If you are unsure where to find it, please contact us using the email address below.

More technical documentation for future developers and maintainers can be found in the documentation folder.

Future versions of this tool will increase the supporting information available in the validation output report, for example by listing the exact set of checks run for each variable.

## Contact

metadata.validation.tool@ons.gov.uk

Please contact us if you wish to report any issues or bugs, or to request features. Which tables of the output report were most useful? Did you prefer the aggregated tables, or the commented version with individual cells highlighted?

Also, we cannot currently guarantee that there will be no false positives or false negatives in the output, so your feedback is very valuable!

Please also contact us if you are using this tool and haven't yet spoken to us, the developers. We wish to keep in contact with our community of users.

# Using the tool

## Installation

*The commands below are for use in a command prompt terminal, such as Anaconda Powershell.*

To install this package:
`pip3 install ons-metadata-validation`

## Basic usage

Default settings have been set so that a general non-technical user will not often need to specify optional parameters.

The only parameter that must be specified each time the tool is used is the location of the filled metadata template to validate. This can be specified as an absolute or relative path.

Thus, to use as CMAR with all default settings:
`python3 -m ons_metadata_validation "path/to/file.xlsx"`

This will produce an excel file reporting on failed validation checks. It will be saved in the same folder as the input file.

Note that the tool will not be able to 'see' files on SharePoint. You will need to either map your sharepoint location to a drive, or download the filled template file first.

Note that the ability to process all metadata templates in a specified folder is planned for a future release.

## Optional configurations

Optional parameters always come after the filename when calling the command.

### variable_check_set
This tool is designed for users of at various pipeline stages and in various contexts. Some template variables are populated later, and therefore might not exist yet for upstream users. This parameter is used to select the appropriate set of variables to check.

* default: "cmar"
* choices: ["cmar", "full"]

Example:
    `python3 -m ons_metadata_validation "path/to/file.xlsx" variable_check_set="full"`

### save_report
Whether or not to save the output report.

* default: True
* choices: True, False

Example:
    `python3 -m ons_metadata_validation "path/to/file.xlsx" save_report=False`

### save_commented_copy
Whether or not to save a copy of the metadata template with invalid cells highlighted and commented. Please note that you must then update and resubmit the original file - do not edit and submit this copy!

* default: True
* choices: True, False

Example:
    `python3 -m ons_metadata_validation "path/to/file.xlsx" save_commented_copy=True`

### save_corrected_copy
Some simple validation issues, such as missing full stops, double spaces, or trailing whitespace, can be fixed programmatically. Setting this parameter to True will save an edited copy of the original file.

* default: True
* choices: True, False

Example:
    `python3 -m ons_metadata_validation "path/to/file.xlsx" save_corrected_copy=True`


### destination_folder
By default, all outputs are saved in the same folder as the input file. However, you can specify a different location if you wish. This is only for specifying the output folder; the *names* of individual outputs combine the input file's name with a description indicating the type of output.

* default: None

Example:
    `python3 -m ons_metadata_validation "path/to/file.xlsx" destination_folder="some/other/directory"`

# Reading the output report

## Hard and soft checks

Validation checks are considered to be "hard" or "soft". 
		
Hard checks are conditions that must be satisfied for the ingest pipeline to work successfully. Failing a hard check means that action must be taken before the metadata form can be submitted.	For example, a hard check may inspect whether a mandatory field contains an expected and machine-readable value, without leading or trailing whitespace.
		
Soft checks are checks that require inspection, but not necessarily action, if they fail. Though they are still important for high quality metadata, they won't prevent a minimum successful ingest. For example, a soft check may inspect the format and style of a field to ensure that it is useful and legible to humans.

In the commented output, cells containing *any* hard check fails are colour coded in orange. They may also contain soft check fails.

Cells containing *only* soft check fails are highlighted in yellow.

## Comparative checks

Most checks only care about single values and thus only need to look at one cell at a time. Others require information from all the cells in a column; multiple columns in a row; or multiple sheets across the template.

Comparative checks involve more than one cell value at a time. For example, a column of table names might require that each name be unique within that column. Or, for consistency, a table name appearing on one sheet might be required to also appear on a list of tables from a previous sheet.

Comparative checks are also either hard or soft, as defined above.

## Output tables

| Sheet                         | Variables          | Checks        | Description                                                                                                                                     |
|-------------------------------|--------------------|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| single_validation_checks      | All                | Hard and Soft | Summarises checks that care only about single cell values at a time. Details the checks employed during this run, pass or fail.             |
| rowwise_validations           | All                | Comparative   | Summarises comparative checks that look along whole rows of metadata. Details the checks employed during this run, pass or fail.            |
| comparative_validations       | All                | Comparative   | Summarises comparative checks that look across multiple tabs. Details the checks employed during this run, pass or fail.                    |
| Short % overview              | Mandatory only     | Hard and Soft | Each row is a tab & variable name combination; columns list the % of records that are missing or failed a) any hard or b) only soft checks. |
| Long % overview               | Mandatory only     | Hard and Soft | Each row is a tab & variable name combination; columns are fail %s for every check. This tab is still in development.                       |
| Fails by value                | All                | Hard and Soft | Each row details a value appearing in a variable, all the cells that value appears in, and all the hard and soft checks that value fails.   |
| Fails by cell - Mandatory     | Mandatory only     | Hard and Soft | Each row details the names of all hard and soft checks failed by a single cell in a mandatory field.                                          |
| Fails by check - Hard         | All                | Hard          | Each row details the cells of a single variable that have failed a particular hard check.                                                     |
| Missing values                | All mandatory      | Missingness   | each row details the cells with missing values for a single variable.                                                                         |
| Comparative check fails       | All                | Comparative   | Each row details one instance of a failed comparative check.                                                                                  |
| Fails by cell - Non Mandatory | Non-mandatory only | Hard and Soft | Each row details the names of all hard and soft checks failed by a single cell in a non-mandatory (optional or conditional) field.          |
| Fails by check - Soft         | All                | Soft          | Each row details the cells of a single variable that have failed a particular soft check.                                                     |

## Note regarding comparative checks

It can be hard to decide where and how to flag comparative check failures. For example, if a column should contain only unique values but contains duplicates, each cell containing a duplicate should be flagged.

# Human inspection: checks not covered by this tool

As mentioned above, **the use of this tool is not a substitute for human involvement in the validation process**. Do not solely trust in this tool to detect all and only the validation issues on your metadata form.

* Many fields, such as descriptions and notes, contain free text. These should be read by a human to ensure that they are intelligible, useful, and appropriate.

* The tool inspects urls and email addresses provided on the metadata form solely in terms of whether their string format is plausible. It cannot check whether their destinations are active, correct, and publicly accessible.

* Dataset, table, and file names ought to be concise and meaningfully descriptive of the data contained within. Naming standards for GCP objects are available internally on SharePoint.

* The tool, and the guidance, discourage acronyms and abbreviations, for the sake of clarity. However, acronyms that are widely understood, such as UK and NHS, are permissible. Judgement may be needed when acronyms and abbreviations are nonetheless needed due to character limits or brevity in free text.

* In general, the tool focuses on validation limitations where certain responses are 100% unacceptable or impossible, such as a precision of 0. Human assessment is required when values are *implausible* but still *possible*, such as suspiciously large numbers of files / header rows / etc.

# Known bugs and issues

* Expression of cell ranges on some of the tabular output sheets are unintentionally duplicated.

* Checks that handle short and long date formats do not produce intended results for certain inputs.

# Version conversion

As a supplementary feature, this repo contains functions for upgrading template versions, e.g. from v1 or v2 to v3.

This feature can also be used to *downgrade* from v3 to v2.

**After converting a template, please also run the main function to validate the result!**


## Setup

* After installing the repo as explained above, you can import this function in your IDE of choice:
`from ons_metadata_validation.processing.convert_to_version import convert_template_to_version`

* To run this function, you will need access to a blank copy of the 3.0 excel template. This can be found on SharePoint. If you don't know where to find it, ask us or a colleague.

## Docstring

The docsting of this function is replicated here for your convenience.

"""Convert a metadata template to another version.

    Args:
        orig_path (str): Path to the original template. Version is inferred.
        empty_target_path (str): Path to the empty dst template.
        save_path (str): Where to save the dst template.
        target_version (float, optional): The version to transform to. Defaults to 3.0.
        default_values (Dict, optional): Default values to populate the template with. Defaults to None.
        apply_autofixes (bool, optional): Apply autofixes before converting to V3 template. Defaults to False.

    Returns:
        bool: True if successful. False otherwise.

    Notes:
        Please also run the main function to validate the results of your conversion!

    Example:
    >>> convert_template_to_version(
    >>>     "path/to/original_v1/template.xlsx",
    >>>     "path/to/empty_v3/template.xlsx",
    >>>     "path/where/to/save/v3/template.xlsx",
    >>>     target_version=3,
    >>>     default_values={
    >>>         'DATASET_access_level': "Access level 3",
    >>>         "DATASET_safe_settings": "ESRC SafePods, Assured Organisational Connectivity (office-based), Assured Organisational Connectivity (homeworking)",
    >>>         "DATASET_subject_to_low_level_access_control": "No",
    >>>         "VARS_variable_availability": "Standard",
    >>>         "VARS_row_level_restrictions": "No"
    >>>     }
    >>> )
    """

## Referring to tabs & variables

In order to set default values, you will need to identify fields of the metadata template by using the tool's machine-readable terms. Start with the tab name, followed by an underscore:

| Spreadsheet name | Code name |
|------------------|---------|
| Dataset Resource | DATASET |
| Dataset Series   | SERIES  |
| Dataset File     | FILE    |
| Variables        | VARS    |
| Codes and Values | CODES   |
| Back Office      | DATASET |

Then add the variable name:

* Replace all capitals in the name with lower case.
* Replace all spaces with underscores. 
* Replace special characters like apostrophes, brackets, slashes, and question marks with underscores. 
* If the name *ends* with a special character, just drop it instead.

Examples: 

* "Is this a code?" on the "Variables" tab is internally referenced as "VARS_is_this_a_code".
* "Data Contributor(s)" on the "Dataset Resource" tab is internally referenced as "DATASET_data_contributor_s".


## Notes

* As of release 1.2.0, you can now also convert v1 templates to later versions.