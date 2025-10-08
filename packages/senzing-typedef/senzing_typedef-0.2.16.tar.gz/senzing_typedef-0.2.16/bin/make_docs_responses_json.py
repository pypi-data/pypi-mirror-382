#! /usr/bin/env python3

# pylint: disable=duplicate-code

"""
For more information, visit https://jsontypedef.com/docs/python-codegen/
"""

import json

DEFINITIONS = {}
GLOBAL_OUTPUT_DIRECTORY = "./docs/responses-json"
VARIABLE_JSON_KEY = "user_defined_json_key"
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


def handle_json_elements(json_value):
    """Unwrap an RFC8927 'element'."""
    elements = json_value.get("elements", {})
    result = recurse_json(elements)
    return [result]


def handle_json_metadata(json_value):
    """Unwrap an RFC8927 'metadata'."""
    metadata = json_value.get("metadata")
    python_type = metadata.get("pythonType")
    if python_type:
        return handle_json_python_type(python_type)
    return None


def handle_json_properties(json_value):
    """Unwrap an RFC8927 'properties'."""
    result = {}
    properties = json_value.get("properties", {})
    for key, value in properties.items():
        result[key] = recurse_json(value)
    return result


def handle_json_python_type(python_type):
    """Unwrap based on custom datatype."""

    result = {}

    match python_type:
        case "Dict[str, List[FeatureScoreForAttribute]]":
            result = {VARIABLE_JSON_KEY: [recurse_json(DEFINITIONS.get("FeatureScoreForAttribute"))]}
        case "Dict[str, List[FeatureDescriptionValue]]":
            result = {VARIABLE_JSON_KEY: [recurse_json(DEFINITIONS.get("FeatureDescriptionValue"))]}
        case "Dict[str, List[FeatureForAttribute]]":
            result = {VARIABLE_JSON_KEY: [recurse_json(DEFINITIONS.get("FeatureForAttribute"))]}
        case "Dict[str, List[FeatureForAttributes]]":
            result = {VARIABLE_JSON_KEY: [recurse_json(DEFINITIONS.get("FeatureForAttributes"))]}
        case "Dict[str, List[FeatureForGetEntity]]":
            result = {VARIABLE_JSON_KEY: [recurse_json(DEFINITIONS.get("FeatureForGetEntity"))]}
        case "Dict[str, List[MatchInfoForAttribute]]":
            result = {VARIABLE_JSON_KEY: [recurse_json(DEFINITIONS.get("MatchInfoForAttribute"))]}
        case "Dict[str, int]":
            result = {
                VARIABLE_JSON_KEY: "int32",
            }
        case "Dict[str, object]":
            result = {
                VARIABLE_JSON_KEY: "object",
            }
        case "Dict[str, str]":
            result = {
                VARIABLE_JSON_KEY: "string",
            }
        case "object":
            result = "object"
        case "string":
            result = "string"
        case _:
            print(f"Error: Bad 'pythonType:' {python_type}")
            raise NotImplementedError
    return result


def handle_json_ref(json_value):
    """Unwrap an RFC8927 'ref'."""
    return recurse_json(DEFINITIONS.get(json_value.get("ref")))


def handle_json_type(json_value):
    """Unwrap an RFC8927 'type'."""
    return json_value.get("type")


def handle_json_values(json_value):
    """Unwrap an RFC8927 'value'."""
    ref_type = json_value.get("values", {}).get("ref")
    if not ref_type:
        ref_type = json_value.get("values", {}).get("type")

    if ref_type in ["int32", "string"]:
        result = {VARIABLE_JSON_KEY: ref_type}
    elif ref_type:
        result = {VARIABLE_JSON_KEY: recurse_json(DEFINITIONS.get(ref_type))}
    else:
        result = {VARIABLE_JSON_KEY: recurse_json(json_value.get("values", {}))}
    return result


def recurse_json(json_value):
    """Do recursive descent through the JSON/dictionary."""

    result = {}

    if "metadata" in json_value:
        result = handle_json_metadata(json_value)
        if result:
            return result

    if "type" in json_value:
        result = handle_json_type(json_value)

    if "values" in json_value:
        result = handle_json_values(json_value)

    if "ref" in json_value:
        result = handle_json_ref(json_value)

    if "properties" in json_value:
        result = handle_json_properties(json_value)

    if "elements" in json_value:
        result = handle_json_elements(json_value)

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

    final_result = recurse_json(initial_json_value)

    output_file = f"{GLOBAL_OUTPUT_DIRECTORY}/{requested_json_key}.json"
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(final_result, json_file, indent=4)
