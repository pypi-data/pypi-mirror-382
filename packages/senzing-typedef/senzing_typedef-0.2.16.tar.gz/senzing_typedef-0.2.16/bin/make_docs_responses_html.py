#! /usr/bin/env python3

# pylint: disable=duplicate-code

"""
For more information, visit https://jsontypedef.com/docs/python-codegen/
"""

import json

VARIABLE_JSON_KEY = "user_defined_json_key"
DEFINITIONS = {}
INDENT = "&nbsp;&nbsp;&nbsp;&nbsp;"

GLOBAL_OUTPUT_DIRECTORY = "./docs/responses-html"
GLOBAL_JSON_KEYS = [
    "SzConfigExportResponse",
    "SzConfigGetDataSourceRegistryResponse",
    "SzConfigManagerGetConfigRegistryResponse",
    "SzConfigRegisterDataSourceResponse",
    "SzDiagnosticCheckRepositoryPerformanceResponse",
    "SzDiagnosticGetFeatureResponse",
    "SzDiagnosticGetRepositoryInfoResponse",
    "SzEngineAddRecordResponse",
    "SzEngineDeleteRecordResponse",
    "SzEngineExportCsvEntityReportCsvColumnList",
    "SzEngineFetchNextResponse",
    "SzEngineFindInterestingEntitiesByEntityIdResponse",
    "SzEngineFindInterestingEntitiesByRecordIdResponse",
    "SzEngineFindNetworkByEntityIdEntityIds",
    "SzEngineFindNetworkByEntityIdResponse",
    "SzEngineFindNetworkByRecordIdRecordKeys",
    "SzEngineFindNetworkByRecordIdResponse",
    "SzEngineFindPathByEntityIdAvoidEntityIds",
    "SzEngineFindPathByEntityIdRequiredDataSources",
    "SzEngineFindPathByEntityIdResponse",
    "SzEngineFindPathByRecordIdAvoidRecordKeys",
    "SzEngineFindPathByRecordIdRequiredDataSources",
    "SzEngineFindPathByRecordIdResponse",
    "SzEngineGetEntityByEntityIdResponse",
    "SzEngineGetEntityByRecordIdResponse",
    "SzEngineGetRecordPreviewResponse",
    "SzEngineGetRecordResponse",
    "SzEngineGetRedoRecordResponse",
    "SzEngineGetStatsResponse",
    "SzEngineGetVirtualEntityByRecordIdRecordKeys",
    "SzEngineGetVirtualEntityByRecordIdResponse",
    "SzEngineHowEntityByEntityIdResponse",
    "SzEngineProcessRedoRecordResponse",
    "SzEngineReevaluateEntityResponse",
    "SzEngineReevaluateRecordResponse",
    "SzEngineSearchByAttributesAttributes",
    "SzEngineSearchByAttributesResponse",
    "SzEngineSearchByAttributesSearchProfile",
    "SzEngineStreamExportJsonEntityReportResponse",
    "SzEngineWhyEntitiesResponse",
    "SzEngineWhyRecordInEntityResponse",
    "SzEngineWhyRecordsResponse",
    "SzEngineWhySearchAttributes",
    "SzEngineWhySearchResponse",
    "SzEngineWhySearchSearchProfile",
    "SzProductGetLicenseResponse",
    "SzProductGetVersionResponse",
]

# -----------------------------------------------------------------------------
# Functions to process RFC8927.json file and create SCHEMA variable.
# -----------------------------------------------------------------------------


def handle_json_dict(level, key, description, json_key):
    """Unwrap a dictionary."""
    result = make_json_key(key, description, "{")
    result += recurse_json(level + 1, VARIABLE_JSON_KEY, DEFINITIONS.get(json_key, {}))[:-1]
    result += html_println(level, "},")
    return html_println(level, result)


def handle_json_dict_data_type(level, key, description, data_type):
    """Unwrap a dictionary."""
    result = make_json_key(key, description, "{")
    result += html_println(level + 1, f'"{VARIABLE_JSON_KEY}": "{data_type}"')
    result += html_println(level, "},")
    return html_println(level, result)


def handle_json_dict_list(level, key, description, json_key):
    """Unwrap a dictionary of keyed lists."""
    result = make_json_key(key, description, "{")
    result += html_println(level + 1, f'"{VARIABLE_JSON_KEY}": [')
    result += recurse_json(level + 2, None, DEFINITIONS.get(json_key, {}))[:-1]
    result += html_println(level + 1, "]")
    result += html_println(level, "},")
    return html_println(level, result)


def handle_json_elements(level, key, value) -> str:
    """Unwrap an RFC8927 'element'."""
    elements = value.get("elements", [])
    description = value.get("metadata", {}).get("description")
    result = html_println(level, make_json_key(key, description, "["))
    result += recurse_json(level + 1, None, elements)[:-1]
    result += html_println(level, "],")
    return result


def handle_json_metadata(level, key, json_value) -> str:
    """Unwrap an RFC8927 'metadata'."""
    result = ""
    metadata = json_value.get("metadata", {})
    python_type = metadata.get("pythonType")
    if python_type:
        description = metadata.get("description")
        result += handle_json_python_type(level, key, description, python_type)
    return result


def handle_json_properties(level, key, json_value) -> str:
    """Unwrap an RFC8927 'properties'."""
    properties = json_value.get("properties", {})
    description = json_value.get("metadata", {}).get("description")
    result = html_println(level, make_json_key(key, description, "{"))
    for item_key, item_value in properties.items():
        result += recurse_json(level + 1, item_key, item_value)
    result = result[:-1]
    result += html_println(level, "},")
    return result


def handle_json_python_type(level, key, description, value) -> str:
    """Unwrap based on custom datatype."""

    result = ""
    python_type = value.get("metadata", {}).get("pythonType")
    match python_type:
        case "Dict[str, List[FeatureScoreForAttribute]]":
            result = handle_json_dict_list(level, key, description, "FeatureScoresForAttribute")
        case "Dict[str, List[FeatureDescriptionValue]]":
            result = handle_json_dict_list(level, key, description, "FeatureDescriptionValue")
        case "Dict[str, List[FeatureForAttribute]]":
            result = handle_json_dict_list(level, key, description, "FeatureForAttribute")

        case "Dict[str, List[FeatureForAttributes]]":
            result = handle_json_dict_list(level, key, description, "FeatureForAttributes")
        case "Dict[str, List[FeatureForGetEntity]]":
            result = handle_json_dict_list(level, key, description, "FeatureForGetEntity")
        case "Dict[str, List[MatchInfoForAttribute]]":
            result = handle_json_dict_list(level, key, description, "MatchInfoForAttribute")
        case "Dict[str, int]":
            result = handle_json_dict_data_type(level, key, description, "int32")
        case "Dict[str, object]":
            result = handle_json_dict_data_type(level, key, description, "object")
        case "Dict[str, str]":
            result = handle_json_dict_data_type(level, key, description, "string")
        case "object":
            result = html_println(level, f'"{key}": "object",')
        case "string":
            result = html_println(level, f'"{key}": "string",')
        case "int32":
            result = html_println(level, f'"{key}": "int32",')
        case _:
            print(f"Error: Bad 'pythonType:' {value}")
            raise NotImplementedError

    return result


def handle_json_ref(level, key, value) -> str:
    """Unwrap an RFC8927 'ref'."""
    return recurse_json(level, key, DEFINITIONS.get(value.get("ref")))


def handle_json_type(level, key, value) -> str:
    """Unwrap an RFC8927 'type'."""
    data_type = value.get("type")
    description = value.get("metadata", {}).get("description")

    # html_value = ""
    # if description and key:
    #     html_value += f'"{data_type} - {description}",'
    # else:
    #     html_value += f'"{data_type}",'
    html_value = f'"{data_type}",'

    json_key = make_json_key(key, description, html_value)

    return html_println(level, json_key)


def handle_json_values(level, key, value) -> str:
    """Unwrap an RFC8927 'value'."""
    ref_type = value.get("values", {}).get("ref")
    if not ref_type:
        ref_type = value.get("values", {}).get("type")
    description = value.get("metadata", {}).get("description")

    result = make_json_key(key, description, "{")
    if ref_type in ["int32", "string"]:
        result += html_println(level + 1, f'"{VARIABLE_JSON_KEY}": "{ref_type}"')
    elif ref_type:
        result += recurse_json(level + 1, VARIABLE_JSON_KEY, DEFINITIONS.get(ref_type, {}))[:-1]
    else:
        result += recurse_json(level + 1, VARIABLE_JSON_KEY, value.get("values", {}))[:-1]

    result += html_println(level, "},")

    return html_println(level, result)


def html_println(level, message) -> str:
    """Return a string that prepends an HTML newline to the message."""
    # return f'\n<br/><span style="width: {50 * level}px; display: inline-block"></span>{message}'
    return f"\n<br/>{INDENT * level}{message}"


def make_json_key(key, description, suffix) -> str:
    """Create a JSON key with or without an HTML anchor."""
    result = suffix
    if description and key:
        result = (
            f'"<a href="#" data-toggle="tooltip" data-placement="bottom" title="{description}">{key}</a>": {suffix}'
        )
    elif key:
        result = f'"{key}": {suffix}'
    return result


def recurse_json(level, key, value) -> str:
    """Do recursive descent through the JSON/dictionary."""

    result = ""
    if value.get("metadata", {}).get("pythonType"):
        result += handle_json_python_type(level, key, value.get("metadata", {}).get("description"), value)
    elif "type" in value:
        result += handle_json_type(level, key, value)
    elif "values" in value:
        result += handle_json_values(level, key, value)
    elif "ref" in value:
        result += handle_json_ref(level, key, value)
    elif "properties" in value:
        result += handle_json_properties(level, key, value)
    elif "elements" in value:
        result += handle_json_elements(level, key, value)
    elif "metadata" in value:
        result += handle_json_metadata(level, key, value)

    return result


# -----------------------------------------------------------------------------
# --- Make HTML
# -----------------------------------------------------------------------------


def make_html(title: str, input_dict: dict) -> str:
    """Create an HTML string."""

    # HTML prefix.

    result = """<!DOCTYPE html>
<html>
<head>
    <style>
        body {background-color: White;}
        .code-block {font-family: "Courier New", Courier, monospace; background-color: LightGrey;}
    </style>
"""

    result += f"    <title>{title}</title>"

    result += """
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
</head>
<body>
"""

    result += f"<h1>{title}</h1>"
    result += """
<div class="code-block">"""

    # HTML body.

    result += recurse_json(0, None, input_dict)[:-1]

    # HTML suffix.

    result += """
<br/>&nbsp;
</div>
</body>
</html>
"""

    return result


# -----------------------------------------------------------------------------
# --- Main
# -----------------------------------------------------------------------------

# Read JSON from file.

INPUT_FILENAME = "./senzingsdk-RFC8927.json"
with open(INPUT_FILENAME, "r", encoding="utf-8") as input_file:
    DATA = json.load(input_file)

DEFINITIONS = DATA.get("definitions", {})

# Recurse through dictionary.

for requested_json_key in GLOBAL_JSON_KEYS:
    initial_json_value = DEFINITIONS.get(requested_json_key)

    # Short-circuit when JSON key not found.

    if initial_json_value is None:
        print(f"Could not find JSON key: {requested_json_key}")
        continue

    html = make_html(requested_json_key, initial_json_value)

    output_file = f"{GLOBAL_OUTPUT_DIRECTORY}/{requested_json_key}.html"
    with open(output_file, "w", encoding="utf-8") as json_file:
        json_file.write(html)
