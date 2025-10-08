#! /usr/bin/env python3

"""
Work-in-progress: Determine what JSON keys are not used.
For more information, visit https://jsontypedef.com/docs/python-codegen/
"""

# pylint: disable=duplicate-code

import json
import os
from pathlib import Path

DEFINITIONS = {}
INPUT_DIRECTORY = "./testdata/responses_senzing"
INPUT_FILENAME = "./senzingsdk-RFC8927.json"
OUTPUT_FILENAME = "./docs/unused_json_keys.json"
RESIDUAL = {}
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
# Functions to process RFC8927.json file and create DEFINITIONS variable.
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
# ---
# -----------------------------------------------------------------------------


# def remove_keys(haystack, needles):
#     """Remove keys from haystack that exist in needles."""
#     return {k: v for k, v in haystack.items() if k not in needles}


# def remove_keys_recursively(haystack, needles):
#     """Remove keys from haystack that exist in needles."""
#     result = {}
#     for key, value in haystack.items():
#         if key not in needles:
#             if isinstance(value, dict):
#                 result[key] = remove_keys_recursively(value, needles)
#             else:
#                 result[key] = value
#     return result


# def remove_json(needles, haystack):

#     if isinstance(needles, dict):
#         if isinstance(haystack, dict):
#             for key, value in needles.items():
#                 if key not in haystack:
#                     return
#                 haystack = remove_json(value, haystack.get(key))
#     return haystack


# def remove_keys_recursive01(json_key, needles, haystack):
#     """Remove keys from dict1 (and nested dicts) that exist in dict2"""
#     result = None

#     if isinstance(needles, dict):
#         result = {}
#         for key, value in needles.items():
#             new_haystack = None
#             if isinstance(haystack, dict):
#                 new_haystack = haystack.get(key)
#             new_result = remove_keys_recursive(key, value, new_haystack)
#             if new_result:
#                 result[key] = new_result

#     if isinstance(needles, list):
#         result = []
#         new_haystack = None
#         if isinstance(haystack, list):
#             new_haystack = haystack[0]
#         for value in needles:
#             new_result = remove_keys_recursive("", value, new_haystack)
#             if new_result:
#                 result.append(new_result)
#     return result


# def remove_keys_recursiveX(needles, haystack):
#     """Remove keys from dict1 (and nested dicts) that exist in dict2"""
#     result = None

#     if isinstance(needles, dict):
#         result = {}
#         if isinstance(haystack, dict):
#             for key, value in haystack.items():
#                 if key in needles:
#                     new_result = remove_keys_recursive(needles.get(key), value)
#                     if new_result:
#                         result[key] = new_result
#                 else:
#                     result[key] = value

#     if isinstance(needles, list):
#         result = []
#         new_haystack = None
#         if isinstance(haystack, list):
#             new_haystack = haystack[0]
#         for value in needles:
#             new_result = remove_keys_recursive(value, new_haystack)
#             if new_result:
#                 if new_result not in result:
#                     result.append(new_result)

#     return result


def remove_keys_recursive(needles, haystack):
    """Remove keys from dict1 (and nested dicts) that exist in dict2"""
    result = None

    if isinstance(needles, dict):
        result = {}
        if isinstance(haystack, dict):
            for key, value in haystack.items():
                if key in needles:
                    result_value = remove_keys_recursive(needles.get(key), value)
                    if result_value:
                        result[key] = result_value
                elif key == VARIABLE_JSON_KEY:
                    for needle_value in needles.values():
                        value = remove_keys_recursive(needle_value, value)
                    if value:
                        result[key] = value
                else:
                    if value:
                        result[key] = value

    if isinstance(needles, list):
        result = []
        new_haystack = []
        if isinstance(haystack, list):
            if len(haystack) > 0:
                new_haystack = haystack[0]
        for value in needles:
            new_result = remove_keys_recursive(value, new_haystack)
            if new_result:
                if new_result not in result:
                    result.append(new_result)

    return result


# -----------------------------------------------------------------------------
# --- Main
# -----------------------------------------------------------------------------

# Read JSON from file.

with open(INPUT_FILENAME, "r", encoding="utf-8") as input_file:
    DATA = json.load(input_file)

DEFINITIONS = DATA.get("definitions", {})

# Go through test files.

# test_file_names = os.listdir(INPUT_DIRECTORY)
test_file_names = ["SzEngineWhyRecordsResponse.jsonl"]
for test_file_name in test_file_names:
    requested_json_key = Path(test_file_name).stem
    initial_json_value = DEFINITIONS.get(requested_json_key)

    # Short-circuit when JSON key not found.

    if initial_json_value is None:
        print(f"Could not find JSON key: {requested_json_key}")
        continue

    residual_json = recurse_json(initial_json_value)

    with open(os.path.join(INPUT_DIRECTORY, test_file_name), "r", encoding="utf-8") as test_file:
        for line in test_file:
            residual_json = remove_keys_recursive(json.loads(line), residual_json)

    RESIDUAL[requested_json_key] = residual_json

with open(OUTPUT_FILENAME, "w", encoding="utf-8") as json_file:
    json.dump(RESIDUAL, json_file, indent=4)
