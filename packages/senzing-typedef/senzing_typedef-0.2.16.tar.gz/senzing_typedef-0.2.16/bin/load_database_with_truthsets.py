#! /usr/bin/env python3

# pylint: disable=duplicate-code

"""
load_database_with_truthsets.py

Load the truth-set data in ../testdata/truthsets/ into a
SQLite database at /tmp/sqlite/G2C.db

"""

import json
import os
import pathlib

from senzing import SzAbstractFactory, SzEngineFlags, SzError
from senzing_core import SzAbstractFactoryCore

# -----------------------------------------------------------------------------
# Add records.
# -----------------------------------------------------------------------------


def add_records(sz_abstract_factory: SzAbstractFactory):
    """Add records to the Senzing repository."""
    sz_engine = sz_abstract_factory.create_engine()

    # Add records.

    filenames = [
        "customers.jsonl",
        "reference.jsonl",
        "watchlist.jsonl",
    ]

    current_path = pathlib.Path(__file__).parent.resolve()
    for filename in filenames:
        file_path = os.path.abspath(f"{current_path}/../testdata/truthsets/{filename}")
        with open(file_path, "r", encoding="utf-8") as input_file:
            for line in input_file:
                line_as_dict = json.loads(line)
                data_source = line_as_dict.get("DATA_SOURCE")
                record_id = line_as_dict.get("RECORD_ID")
                sz_engine.add_record(data_source, record_id, line, SzEngineFlags.SZ_WITH_INFO)


def create_sz_abstract_factory() -> SzAbstractFactory:
    """Create an SzAbstractFactory."""
    instance_name = "Example"
    settings = {
        "PIPELINE": {
            "CONFIGPATH": "/etc/opt/senzing",
            "RESOURCEPATH": "/opt/senzing/er/resources",
            "SUPPORTPATH": "/opt/senzing/data",
        },
        "SQL": {"CONNECTION": "sqlite3://na:na@/tmp/sqlite/G2C.db"},
    }

    try:
        sz_abstract_factory = SzAbstractFactoryCore(instance_name, settings)
    except SzError as err:
        print(f"\nERROR: {err}\n")

    return sz_abstract_factory


def register_datasources(sz_abstract_factory: SzAbstractFactory):
    """Add Data Sources to the Senzing repository."""
    sz_config_manager = sz_abstract_factory.create_configmanager()

    # Register datasources.

    current_config_id = sz_config_manager.get_default_config_id()
    sz_config = sz_config_manager.create_config_from_config_id(current_config_id)

    for data_source in ("CUSTOMERS", "REFERENCE", "WATCHLIST"):
        sz_config.register_data_source(data_source)

    new_config = sz_config.export()
    new_config_id = sz_config_manager.register_config(new_config, "load_database_with_truthsets.py")
    sz_config_manager.replace_default_config_id(current_config_id, new_config_id)
    sz_abstract_factory.reinitialize(new_config_id)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    the_sz_abstract_factory = create_sz_abstract_factory()
    register_datasources(the_sz_abstract_factory)
    add_records(the_sz_abstract_factory)
