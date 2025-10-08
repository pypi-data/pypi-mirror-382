#! /usr/bin/env python3

"""
Requires minimum Python 3.10
"""

import builtins
import json
import logging
import os
import sys
from pathlib import Path

# Tricky code:  Need to import all python.typedef.* for the "not in globals()" test
# pylint: disable=unused-wildcard-import

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from python import senzing_typedef  # pylint: disable=wrong-import-position
from python.senzing_typedef import *  # pylint: disable=wrong-import-position disable=wildcard-import

INPUT_DIRECTORY = "./testdata/responses_senzing"
DEBUG = False
ERROR_COUNT = 0
TEST_COUNT = 0

PYTHON_CLASS_MAP = {
    "SzEngineFindInterestingEntitiesByEntityIdResponse": "SzEngineFindInterestingEntitiesByEntityIDResponse",
    "SzEngineFindInterestingEntitiesByRecordIdResponse": "SzEngineFindInterestingEntitiesByRecordIDResponse",
    "SzEngineFindNetworkByEntityIdResponse": "SzEngineFindNetworkByEntityIDResponse",
    "SzEngineFindNetworkByRecordIdResponse": "SzEngineFindNetworkByRecordIDResponse",
    "SzEngineFindPathByEntityIdResponse": "SzEngineFindPathByEntityIDResponse",
    "SzEngineFindPathByRecordIdResponse": "SzEngineFindPathByRecordIDResponse",
    "SzEngineGetEntityByEntityIdResponse": "SzEngineGetEntityByEntityIDResponse",
    "SzEngineGetEntityByRecordIdResponse": "SzEngineGetEntityByRecordIDResponse",
    "SzEngineGetVirtualEntityByRecordIdResponse": "SzEngineGetVirtualEntityByRecordIDResponse",
    "SzEngineHowEntityByEntityIdResponse": "SzEngineHowEntityByEntityIDResponse",
}

# -----------------------------------------------------------------------------
# --- Monkey patch
# ---   Tricky code!
# -----------------------------------------------------------------------------


def _parse_rfc3339_with_z(s: str) -> str:
    tmp_result = senzing_typedef._parse_rfc3339_original(s)  # pylint: disable=protected-access
    timestamp_with_z = tmp_result.isoformat().replace("+00:00", "Z")
    return timestamp_with_z


senzing_typedef._parse_rfc3339_original = senzing_typedef._parse_rfc3339  # pylint: disable=protected-access
senzing_typedef._parse_rfc3339 = _parse_rfc3339_with_z  # pylint: disable=protected-access

# -----------------------------------------------------------------------------
# --- Functions
# -----------------------------------------------------------------------------


def is_equal(test_name, source, target):
    """Determine if source and target are equal. Return boolean"""

    result = True

    if DEBUG:
        print(test_name)

    if target is None:
        if source is None:
            return True
        return False

    source_type = type(source)
    if source_type == builtins.dict:
        for key, value in source.items():
            if not is_equal(f"{test_name}.{key}", value, target.get(key)):
                return False
    elif source_type == builtins.list:
        source_length = len(source)
        target_length = len(target)
        if source_length != target_length:
            return False
        for item_number in range(source_length):
            if not is_equal(
                f"{test_name}[{item_number}]",
                source[item_number],
                target[item_number],
            ):
                return False
    else:
        if source != target:
            logging.error("JSON key conflict: %s", test_name)
            result = False
    return result


def remove_empty_elements(an_object):
    """Remove empty object from dictionary."""

    def empty(test_object):
        return test_object is None

    source_type = type(an_object)
    if source_type == builtins.dict:
        return {k: v for k, v in ((k, remove_empty_elements(v)) for k, v in an_object.items()) if not empty(v)}
    if source_type == builtins.list:
        return [v for v in (remove_empty_elements(v) for v in an_object) if not empty(v)]
    return an_object


# -----------------------------------------------------------------------------
# --- Main
# -----------------------------------------------------------------------------


if __name__ == "__main__":

    # Set up logging.

    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)

    # Prolog.

    horizontal_rule = format("-" * 80)
    logging.info("%s", horizontal_rule)
    logging.info("--- %s - Begin", format(os.path.basename(__file__)))
    logging.info("%s", horizontal_rule)

    test_file_names = os.listdir(INPUT_DIRECTORY)
    # test_file_names = ["SzEngineWhyRecordsResponse.jsonl"]
    for test_file_name in test_file_names:
        senzing_api_class = Path(test_file_name).stem

        if senzing_api_class not in globals():
            if senzing_api_class in PYTHON_CLASS_MAP:
                senzing_api_class = PYTHON_CLASS_MAP.get(senzing_api_class)
            else:
                ERROR_COUNT += 1
                logging.error("Incorrect pythonClass: %s", senzing_api_class)
                continue

        senzing_class = globals()[senzing_api_class]

        with open(os.path.join(INPUT_DIRECTORY, test_file_name), "r", encoding="utf-8") as test_file:
            LINE_COUNT = 0
            for line in test_file:
                LINE_COUNT += 1
                TEST_COUNT += 1
                LINE_ERRORS = ERROR_COUNT
                TEST_NAME = f"{senzing_api_class}.{LINE_COUNT}"
                line_as_dict = json.loads(line)

                # Test for similarity in key/values.

                json_struct = senzing_class.from_json_data(line_as_dict)
                reconstructed_json_string = json.dumps(json_struct.to_json_data())
                reconstructed_testcase_dict = json.loads(reconstructed_json_string)
                if not is_equal(TEST_NAME, line_as_dict, reconstructed_testcase_dict):
                    ERROR_COUNT += 1
                    logging.error("Not equal Test: %s", TEST_NAME)

                # Test for similarity in JSON string lengths.

                original_json_string_sorted = json.dumps(remove_empty_elements(line_as_dict), sort_keys=True)
                reconstructed_json_string_sorted = json.dumps(
                    remove_empty_elements(json_struct.to_json_data()), sort_keys=True
                )
                len_original = len(original_json_string_sorted)
                len_reconstructed = len(reconstructed_json_string_sorted)
                if len_original != len_reconstructed:
                    ERROR_COUNT += 1
                    logging.error(
                        "Lengths differ: Test: %s; Original: %d; Reconstructed: %d",
                        TEST_NAME,
                        len_original,
                        len_reconstructed,
                    )

                # Test for similarity in JSON strings.

                if original_json_string_sorted != reconstructed_json_string_sorted:
                    for index in range(len_original):
                        if original_json_string_sorted[index] != reconstructed_json_string_sorted[index]:
                            ERROR_COUNT += 1
                            logging.error("Strings differ: Test: %s; First difference position: %d", TEST_NAME, index)
                            logging.error(">>>>>>      Original: %s", original_json_string_sorted)
                            logging.error(">>>>>> Reconstructed: %s", reconstructed_json_string_sorted)
                            break

    # Epilog.

    logging.info("Tests: %d; Errors: %d", TEST_COUNT, ERROR_COUNT)
    logging.info("%s", horizontal_rule)
    logging.info("--- %s - End", os.path.basename(__file__))
    logging.info("%s", horizontal_rule)
    if ERROR_COUNT > 0:
        sys.exit(1)
