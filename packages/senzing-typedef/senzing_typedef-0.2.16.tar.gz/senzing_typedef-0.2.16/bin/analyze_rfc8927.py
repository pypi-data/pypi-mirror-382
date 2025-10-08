#! /usr/bin/env python3

# pylint: disable=duplicate-code

"""
For more information, visit https://jsontypedef.com/docs/python-codegen/
"""

import json

GLOBAL_KEYS = {}
GLOBAL_KEY_COUNT = {}
GLOBAL_KEY_TYPE = {}
GLOBAL_OUT_OF_ORDER = []
GLOBAL_REFS = []
GLOBAL_JSON_KEYS = []
BLACK_LIST = [
    "description",
    "elements",
    "goType",
    "label",
    "metadata",
    "optionalproperties",
    "properties",
    "ref",
    "type",
    "values",
]
USED_KEYS = [
    "RecordKeys",
]
EXCLUDE_LIST = []


def add_to_key_count(key_to_add):
    """Add a key to GLOBAL_KEY_COUNT."""
    if key_to_add not in BLACK_LIST:
        if key_to_add not in GLOBAL_KEY_COUNT:
            GLOBAL_KEY_COUNT[key_to_add] = 1
        else:
            GLOBAL_KEY_COUNT[key_to_add] += 1


def add_to_key_type(key_to_add, value_to_add):
    """Add a key to GLOBAL_KEY_TYPE."""
    if key_to_add not in BLACK_LIST:
        if isinstance(value_to_add, dict):
            if key_to_add not in GLOBAL_KEY_TYPE:
                GLOBAL_KEY_TYPE[key_to_add] = []
            if "type" in value_to_add:
                the_type = value_to_add.get("type")
                if the_type not in GLOBAL_KEY_TYPE[key_to_add]:
                    GLOBAL_KEY_TYPE[key_to_add] += [the_type]
            if "ref" in value_to_add:
                the_ref = value_to_add.get("ref")
                if the_ref not in GLOBAL_KEY_TYPE[key_to_add]:
                    GLOBAL_KEY_TYPE[key_to_add] += [the_ref]


def add_to_list(prefix, list_to_check):
    """Add a key to GLOBAL_KEYS."""
    key_list = [x for x in list_to_check.keys() if x not in BLACK_LIST]
    if len(key_list) > 0:
        key_list.sort()
        GLOBAL_KEYS[prefix] = key_list


def is_sorted(prefix, list_to_check):
    """Determine if list is sorted.  Return boolean"""
    global GLOBAL_OUT_OF_ORDER  # pylint: disable=global-statement
    last_key = ""
    for key_to_check in list_to_check:
        if not normalize(key_to_check) > normalize(last_key):
            GLOBAL_OUT_OF_ORDER += [f"Key out of order: {prefix}.{last_key} > {key_to_check}"]
        last_key = key_to_check


def normalize(input_string):
    """Make a better sortable string."""
    return input_string.replace("_", "Z")


def recurse(prefix, list_to_check):
    """Recurse though dictionary."""
    is_sorted(prefix, list_to_check)
    add_to_list(prefix, list_to_check)
    for key_to_check, value_to_check in list_to_check.items():
        if "ref" in value_to_check:
            ref_value = value_to_check.get("ref")
            if ref_value not in GLOBAL_REFS:
                GLOBAL_REFS.append(ref_value)
        add_to_key_count(key_to_check)
        add_to_key_type(key_to_check, value_to_check)
        if isinstance(value_to_check, dict):
            GLOBAL_JSON_KEYS.append(key_to_check)
            recurse(f"{prefix}.{key_to_check}", value_to_check)


def search_list(search_term):
    """Return a list to compare for identical lists."""
    search_results = []
    search_value = GLOBAL_KEYS.get(search_term)
    for key_to_check, value_to_check in GLOBAL_KEYS.items():
        if key_to_check not in EXCLUDE_LIST:
            if value_to_check == search_value:
                EXCLUDE_LIST.append(key_to_check)
                search_results.append(key_to_check)
    return search_results


# -----------------------------------------------------------------------------
# --- Main
# -----------------------------------------------------------------------------

# Read JSON from file.

INPUT_FILENAME = "./senzingsdk-RFC8927.json"
with open(INPUT_FILENAME, "r", encoding="utf-8") as input_file:
    DATA = json.load(input_file)

# Recurse through dictionary.

recurse("definitions", DATA.get("definitions"))

# Print "out of order" messages.

print("-" * 80)
print("\nTEST 1: Verify that the JSON keys are in sorted order.\n")
if len(GLOBAL_OUT_OF_ORDER) > 0:
    for message in GLOBAL_OUT_OF_ORDER:
        print(message)
else:
    print("Everything is sorted properly.")

# Print missing JSON keys.


# Print result of test for similar lists.

print("")
print("-" * 80)
print("\nTEST 2: Detect lists containing same properties.\n")

for key, value in GLOBAL_KEYS.items():
    EXCLUDE_LIST.append(key)
    results = search_list(key)
    if len(results) > 0:
        print(f"\n{key}:")
        for result in results:
            print(f"  - {result}")

# Print JSON key count results.

print("")
print("-" * 80)
print("\nTEST 3: Count occurrence of JSON keys")
print("\nCOUNT  KEY")
print("-----  -----------------------------")
SORTED_KEY_COUNTS = sorted(GLOBAL_KEY_COUNT.items(), key=lambda x: x[1], reverse=True)
for key, value in SORTED_KEY_COUNTS:
    if value > 1:
        print(f"{value:5d}  {key}")

# Print type/ref variances.

print("")
print("-" * 80)
print("\nTEST 4: Check for JSON keys having different types\n")
SORTED_GLOBAL_KEY_TYPE = dict(sorted(GLOBAL_KEY_TYPE.items()))
for key, value in SORTED_GLOBAL_KEY_TYPE.items():
    if len(value) > 1:
        print(f"{key:30s}  {sorted(value)}")

# Print missing JSON keys that have a ref:

print("")
print("-" * 80)
print("\nTEST 5: Refs without JSON keys.\n")

MISSING_REF_COUNT = 0
for value in GLOBAL_REFS:
    if value not in GLOBAL_JSON_KEYS:
        MISSING_REF_COUNT += 1
        print("Missing:", value)
if MISSING_REF_COUNT == 0:
    print("No missing JSON keys")

# Print result of test for similar lists.
# Must be done last as it mutates GLOBAL_KEYS

print("")
print("-" * 80)
print("\nTEST 6: Detect JSON keys not used.\n")

definitions = GLOBAL_KEYS.pop("definitions")
for key, values in GLOBAL_KEYS.items():
    for value in values:
        if value in definitions:
            definitions.remove(value)
for value in GLOBAL_REFS:
    if value in definitions:
        definitions.remove(value)
USED_KEY_COUNT = 0
for definition in definitions:
    if definition[0:8] not in ["SzConfig", "SzEngine", "SzDiagno", "SzProduc"]:
        if definition not in USED_KEYS:
            USED_KEY_COUNT += 1
            print(definition)
if USED_KEY_COUNT == 0:
    print("All keys used")

# Epilog.

print("")
print("-" * 80)
