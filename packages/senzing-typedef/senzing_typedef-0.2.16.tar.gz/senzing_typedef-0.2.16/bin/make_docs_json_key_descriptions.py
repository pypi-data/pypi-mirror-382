#! /usr/bin/env python3

"""
Create docs/json_key_descriptions.json
"""

import json

INPUT_FILENAME = "./senzingsdk-RFC8927.json"
OUTPUT_FILE = "./docs/json_key_descriptions.json"
JSON_KEYS = {}


def add_description(key, description):
    """Add description to JSON_KEYS dictionary."""
    if not description:
        return
    if key not in JSON_KEYS:
        JSON_KEYS[key] = []
    if description not in JSON_KEYS[key]:
        JSON_KEYS[key].append(description)


def recurse(json_key, json_object):
    """Use recursive descent"""
    match json_object:
        case dict():
            add_description(json_key, json_object.get("metadata", {}).get("description", None))
            for key, value in json_object.items():
                recurse(key, value)
        case list():
            for item in json_object:
                recurse("list", item)


# -----------------------------------------------------------------------------
# --- Main
# -----------------------------------------------------------------------------

# Read input file.

with open(INPUT_FILENAME, "r", encoding="utf-8") as input_file:
    DATA = json.load(input_file)

# Process data.

recurse("", DATA)

# Write output file.

with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
    output_file.write(json.dumps(JSON_KEYS, sort_keys=True, indent=4))
