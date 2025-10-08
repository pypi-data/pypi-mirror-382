#! /usr/bin/env python3

# pylint: disable=duplicate-code

"""
Pretty print the JSON.
"""

import json

BLACK_LIST = [
    "description",
    "elements",
    "goType",
    "metadata",
    "properties",
    "ref",
    "optionalproperties",
    "type",
]
INPUT_FILENAME = "./senzingsdk-RFC8927.json"
OUTPUT_FILENAME = "./senzingsdk-RFC8927-pretty.json"


# -----------------------------------------------------------------------------
# --- Helpers
# -----------------------------------------------------------------------------


def recurse(prefix, an_object):
    """Recurse though the dictionary, beautifying as it goes."""
    for key, value in an_object.items():
        if isinstance(value, dict):
            recurse(f"{prefix}.{key}", value)
            # if key not in BLACK_LIST:
            #     if "metadata" not in value:
            #         value["metadata"] = {}
            #     if "description" not in value.get("metadata"):
            #         value["metadata"]["description"] = "No description."
            #     if "goType" not in value.get("metadata"):
            #         if value.get("type") == "int32":
            #             value["metadata"]["goType"] = "int64"


# -----------------------------------------------------------------------------
# --- Main
# -----------------------------------------------------------------------------

# Read JSON from file.

with open(INPUT_FILENAME, "r", encoding="utf-8") as input_file:
    DATA = json.load(input_file)

# Recurse through dictionary.

# recurse("definitions", DATA.get("definitions"))

# Write JSON to file.

with open(OUTPUT_FILENAME, "w", encoding="utf-8") as output_file:
    json.dump(DATA, output_file, indent=4, sort_keys=True)
