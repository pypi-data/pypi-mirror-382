#! /usr/bin/env python3

# pylint: disable=duplicate-code

"""
Used to generate testdata/*.json
"""

import argparse
import json
import logging
import os

INPUT_FILE = "bin/response-testcases.json"
OUTPUT_FILE = "testdata/responses_generated"

# -----------------------------------------------------------------------------
# --- Helpers
# -----------------------------------------------------------------------------


def canonical_json(json_string):
    """Create compact JSON.  No spaces."""
    result = json.dumps(json_string, sort_keys=True, separators=(",", ":"))
    return result


# -----------------------------------------------------------------------------
# --- Main
# -----------------------------------------------------------------------------

# Set up logging.

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)

# Prolog.

horizontal_rule = format("-" * 80)
logging.info("%s", horizontal_rule)
logging.info("--- %s - Begin", format(os.path.basename(__file__)))
logging.info("%s", horizontal_rule)

# Command line options.

parser = argparse.ArgumentParser(prog="make_testdata_responses_generated.py")
parser.add_argument(
    "--output",
    help=f"Output directory. Default: {OUTPUT_FILE}",
    default=OUTPUT_FILE,
)
args = parser.parse_args()
OUTPUT_DIRECTORY = args.output

# Load testcase metadata.

with open(INPUT_FILE, encoding="utf-8") as input_file:
    response_testcases = json.load(input_file)

# Generate test data.

for senzing_api_class, method_test_cases in response_testcases.items():
    metadata = method_test_cases.get("metadata", {})
    tests = method_test_cases.get("tests", {})
    for test_case_name, test_case_json in tests.items():
        FILENAME = f"{OUTPUT_DIRECTORY}/{senzing_api_class}-{test_case_name}.json"
        with open(FILENAME, "w", encoding="utf-8") as file:
            file.write(canonical_json(test_case_json))

# Epilog.

logging.info("%s", horizontal_rule)
logging.info("--- %s - End", os.path.basename(__file__))
logging.info("%s", horizontal_rule)
