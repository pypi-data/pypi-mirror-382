#! /usr/bin/env python3

"""
Create docs/labels_used.json
"""

import json

INPUT_FILENAME = "./senzingsdk-RFC8927.json"
OUTPUT_FILE = "./docs/json_keys_used.json"
KEYS = {}


def add_to_keys(json_key, path):
    """Add description to LABELS dictionary."""
    if not json_key:
        return
    if json_key in ["", "definitions", "elements", "metadata", "properties", "values", None]:
        return
    if "." not in path:
        return
    if json_key not in KEYS:
        KEYS[json_key] = []
    if path not in KEYS[json_key]:
        KEYS[json_key].append(path)


def recurse(path, json_key, json_object):
    """Use recursive descent"""

    # Determine new_path.

    new_path = ""
    if json_key not in ["", "definitions", "elements", "properties", None]:
        if len(path) > 0:
            new_path = f"{path}.{json_key}"
        else:
            new_path = json_key
    else:
        new_path = path

    # Recurse.

    match json_object:
        case dict():
            add_to_keys(json_key, new_path)
            for key, value in json_object.items():
                recurse(new_path, key, value)
        case list():
            for item in json_object:
                recurse(new_path, "list", item)


# -----------------------------------------------------------------------------
# --- Main
# -----------------------------------------------------------------------------

# Read input file.

with open(INPUT_FILENAME, "r", encoding="utf-8") as input_file:
    DATA = json.load(input_file)

# Process data.

INITIAL_PATH = ""
recurse(INITIAL_PATH, "", DATA)

# Write output file.

with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
    output_file.write(json.dumps(KEYS, sort_keys=True, indent=4))
