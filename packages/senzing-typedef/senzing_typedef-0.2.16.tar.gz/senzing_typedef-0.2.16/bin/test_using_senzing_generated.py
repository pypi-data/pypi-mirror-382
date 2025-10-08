#! /usr/bin/env python3

# pylint: disable=duplicate-code

"""
For more information, visit https://jsontypedef.com/docs/python-codegen/
"""

import json
import os
import sys
from pathlib import Path

# Global variables.

DEBUG = 0
DEFINITIONS = {}
ERROR_COUNT = 0
HR_START = ">" * 80
HR_STOP = "<" * 80
SCHEMA = {}
VARIABLE_JSON_KEY = "<user_defined_json_key>"
INPUT_DIRECTORY = "./testdata/responses_senzing"

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
        case "Dict[str, FeatureScoresForAttribute]":
            return {VARIABLE_JSON_KEY: recurse_json(DEFINITIONS.get("FeatureScoresForAttribute"))}
        case "Dict[str, List[FeatureDescriptionValue]]":
            return {VARIABLE_JSON_KEY: [recurse_json(DEFINITIONS.get("FeatureDescriptionValue"))]}
        case "Dict[str, List[FeatureForAttribute]]":
            return {VARIABLE_JSON_KEY: [recurse_json(DEFINITIONS.get("FeatureForAttribute"))]}
        case "Dict[str, List[FeatureForAttributes]]":
            return {VARIABLE_JSON_KEY: [recurse_json(DEFINITIONS.get("FeatureForAttributes"))]}
        case "Dict[str, List[FeatureForGetEntity]]":
            return {VARIABLE_JSON_KEY: [recurse_json(DEFINITIONS.get("FeatureForGetEntity"))]}
        case "Dict[str, List[MatchInfoForAttribute]]":
            return {VARIABLE_JSON_KEY: [recurse_json(DEFINITIONS.get("MatchInfoForAttribute"))]}
        case "Dict[str, int]":
            return {
                VARIABLE_JSON_KEY: "int32",
            }
        case "Dict[str, object]":
            return {
                VARIABLE_JSON_KEY: "object",
            }
        case "Dict[str, str]":
            return {
                VARIABLE_JSON_KEY: "string",
            }
        case "object":
            return "object"
        case "string":
            return "string"
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
        return handle_json_type(json_value)

    if "values" in json_value:
        return handle_json_values(json_value)

    if "ref" in json_value:
        return handle_json_ref(json_value)

    if "properties" in json_value:
        return handle_json_properties(json_value)

    if "elements" in json_value:
        return handle_json_elements(json_value)

    return result


# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------


def compare_to_schema(test_name, json_path, schema, fragment):
    """Compare a JSON fragment to the schema."""
    global ERROR_COUNT

    debug(2, f"{HR_START}\nSchema for {json_path}:\n{json.dumps(schema)}\n{HR_STOP}\n")

    if isinstance(fragment, list):
        if not isinstance(schema, list):
            ERROR_COUNT += 1
            error_message(test_name, json_path, "Missing list", schema, fragment)
            return
        schema_list = schema[0]
        index = 0
        for x in fragment:
            index += 1
            compare_to_schema(test_name, f"{json_path}.{index}", schema_list, x)
        return

    if isinstance(fragment, dict):
        if not isinstance(schema, dict):
            ERROR_COUNT += 1
            error_message(test_name, json_path, "Missing dict", schema, fragment)
            return
        for key, value in fragment.items():

            schema_value = schema.get(key, {})
            if key not in schema:
                schema_value = schema.get(VARIABLE_JSON_KEY, {})
            compare_to_schema(test_name, f"{json_path}.{key}", schema_value, value)
        return

    if isinstance(fragment, int):
        if schema not in ["int32", "object"]:
            ERROR_COUNT += 1
            error_message(
                test_name,
                json_path,
                "Incorrect specification for int32",
                schema,
                fragment,
            )
        return

    if isinstance(fragment, str):
        if schema not in ["string", "timestamp", "object"]:
            error_message(
                test_name,
                json_path,
                "Incorrect specification for string",
                schema,
                fragment,
            )
        return

    if isinstance(fragment, float):
        if not schema == "float32":
            error_message(
                test_name,
                json_path,
                "Incorrect specification for float32",
                schema,
                fragment,
            )
        return

    if fragment is None:
        return

    # If ending up here, there's an error.

    ERROR_COUNT += 1
    error_message(test_name, json_path, "Unknown value", schema, fragment)


def debug(level, message):
    """If appropriate, print debug statement."""
    if DEBUG >= level:
        print(message)


def error_message(test_name, json_path, message, schema, fragment):
    """Create an error message."""
    output(0, test_name)
    output(1, f"Path: {json_path}")
    output(2, "Error:")
    output(3, message)
    output(3, f"schema: {json.dumps(schema)}")
    output(3, f"  json: {json.dumps(fragment)}")


def is_json_subset(subset_json, full_json):
    """
    Checks if one JSON object (subset_json) is a subset of another (full_json).

    Args:
        subset_json (dict or list): The potential subset JSON.
        full_json (dict or list): The JSON to check against.

    Returns:
        bool: True if subset_json is a subset of full_json, False otherwise.
    """
    if isinstance(subset_json, dict):
        if not isinstance(full_json, dict):
            return False
        for key, value in subset_json.items():
            if key not in full_json:
                return False
            if not is_json_subset(value, full_json[key]):
                return False
        return True

    if isinstance(subset_json, list):
        if not isinstance(full_json, list):
            return False
        for item in subset_json:
            if item not in full_json:
                return False
        return True

    # Primitive types (int, str, bool, float, None)
    return subset_json == full_json


def output(indentation, message):
    """Create an indented message."""
    print(f"{'    ' * indentation}{message}")


def process_rfc8927():
    """Process the RFC8927 JSON."""
    # global DEFINITIONS, SCHEMA
    global DEFINITIONS

    input_filename = "./senzingsdk-RFC8927.json"
    with open(input_filename, "r", encoding="utf-8") as input_file:
        rfc8927 = json.load(input_file)

    DEFINITIONS = rfc8927.get("definitions", {})

    # Recurse through dictionary.

    for requested_json_key in GLOBAL_JSON_KEYS:
        json_value = DEFINITIONS.get(requested_json_key)

        # Short-circuit when JSON key not found.

        if json_value is None:
            print(f"Could not find JSON key: {requested_json_key}")
            continue

        SCHEMA[requested_json_key] = recurse_json(json_value)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


if __name__ == "__main__":

    # Process RFC8927 file to create SCHEMA.

    process_rfc8927()

    test_file_names = os.listdir(INPUT_DIRECTORY)
    # test_file_names = ["SzEngineProcessRedoRecordResponse.jsonl"]
    for test_file_name in test_file_names:
        title = Path(test_file_name).stem
        json_schema = SCHEMA.get(title)

        # Short-circuit when JSON key not found.

        if json_schema is None:
            print(f"Could not find JSON key: {title}")
            continue

        with open(os.path.join(INPUT_DIRECTORY, test_file_name), "r", encoding="utf-8") as test_file:
            LINE_COUNT = 0
            for line in test_file:
                LINE_COUNT += 1
                TEST_NAME = f"{title}.{LINE_COUNT}"
                compare_to_schema(TEST_NAME, title, json_schema, json.loads(line))

    # Epilog.

    if ERROR_COUNT > 0:
        sys.exit(1)
