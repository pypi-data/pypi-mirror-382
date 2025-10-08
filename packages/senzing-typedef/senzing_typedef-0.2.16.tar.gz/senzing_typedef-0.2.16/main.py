#! /usr/bin/env python3

"""
For more information, visit https://jsontypedef.com/docs/python-codegen/
"""

import json
import os
import pathlib

from python.senzing_typedef import (
    SzConfigExportResponse,
    SzConfigGetDataSourceRegistryResponse,
    SzConfigManagerGetConfigRegistryResponse,
    SzConfigRegisterDataSourceResponse,
    SzDiagnosticCheckRepositoryPerformanceResponse,
    SzDiagnosticGetFeatureResponse,
    SzDiagnosticGetRepositoryInfoResponse,
    SzEngineAddRecordResponse,
    SzEngineDeleteRecordResponse,
    SzEngineFindInterestingEntitiesByRecordIDResponse,
    SzEngineFindNetworkByEntityIDResponse,
    SzEngineFindNetworkByRecordIDResponse,
    SzEngineFindPathByEntityIDResponse,
    SzEngineFindPathByRecordIDResponse,
    SzEngineGetEntityByEntityIDResponse,
    SzEngineGetEntityByRecordIDResponse,
    SzEngineGetRecordResponse,
    SzEngineGetRedoRecordResponse,
    SzEngineGetVirtualEntityByRecordIDRecordKeys,
    SzEngineGetVirtualEntityByRecordIDResponse,
    SzEngineHowEntityByEntityIDResponse,
    SzEngineProcessRedoRecordResponse,
    SzEngineReevaluateEntityResponse,
    SzEngineReevaluateRecordResponse,
    SzEngineSearchByAttributesResponse,
    SzEngineWhyEntitiesResponse,
    SzEngineWhyRecordInEntityResponse,
    SzEngineWhyRecordsResponse,
    SzProductGetLicenseResponse,
    SzProductGetVersionResponse,
)

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------


def path_to_testdata(filename: str) -> str:
    """Determine the path to the test data."""
    current_path = pathlib.Path(__file__).parent.resolve()
    result = os.path.abspath(f"{current_path}/testdata/responses_generated/{filename}")
    return result


def file(filename: str) -> dict:
    """Load JSON from file."""
    print(filename)
    absolute_file = path_to_testdata(filename)
    with open(
        absolute_file,
        encoding="utf-8",
    ) as input_file:
        return json.loads(input_file.read())


def print_fmt(response, value):  # pylint: disable=redefined-outer-name eval-used, unused-argument
    """
    Tricky code:
    The "response" passed in needs to be part of the "value" string to be evaluated.
    """
    if value:
        print(f"    {value} = {eval(value)}")  # pylint: disable=eval-used


# -----------------------------------------------------------------------------
# Mock functions - Simulate calls to Senzing SDK API.
# -----------------------------------------------------------------------------


def mock_szengine_add_record_with_info() -> str:
    """Mock call to sz_engine.add_record_with_info()"""
    with open(
        path_to_testdata("SzEngineAddRecordResponse-test-002.json"),
        encoding="utf-8",
    ) as input_file:
        return input_file.read()


def mock_szengine_delete_record_with_info() -> str:
    """Mock call to sz_engine.delete_record_with_info()"""
    with open(
        path_to_testdata("SzEngineDeleteRecordResponse-test-002.json"),
        encoding="utf-8",
    ) as input_file:
        return input_file.read()


def mock_szengine_get_virtual_entity_by_record_id(record_keys, flags: int) -> str:
    """Mock call to sz_engine.get_virtual_entity_by_record_id()"""
    if flags:
        print(f"recordKeys Parameter: {record_keys}\n")

    with open(
        path_to_testdata("SzEngineGetVirtualEntityByRecordIdResponse-test-015.json"),
        encoding="utf-8",
    ) as input_file:
        return input_file.read()


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

# testDict = {}

# testResponse1 = SzEngineGetEntityByEntityIDResponse.from_json_data(testDict)

# x = testResponse1.resolved_entity.features
# y = testResponse1.resolved_entity.feature_ids


# testResponse2 = SzEngineWhyEntitiesResponse.from_json_data(testDict)
# w = testResponse2.why_results[0].entity_id0

# -----------------------------------------------------------------------------
# Demonstrate creating input parameter and parsing output result.
# -----------------------------------------------------------------------------

print("--- Demonstrate creating input parameter and parsing output result ------------\n")

record_keys_dict = {
    "RECORDS": [
        {"DATA_SOURCE": "Unknown", "RECORD_ID": "Unknown"},
        {"DATA_SOURCE": "DATA_SOURCE_2", "RECORD_ID": "RECORD_ID_2"},
    ]
}

record_keys_parameter = SzEngineGetVirtualEntityByRecordIDRecordKeys.from_json_data(record_keys_dict)

record_keys_parameter.records[0].data_source = "DATA_SOURCE_1"
record_keys_parameter.records[0].record_id = "RECORD_ID_1"

# Simulate calling Senzing SDK.

response = mock_szengine_get_virtual_entity_by_record_id(record_keys_parameter.to_json_data(), 1)

# Parse response.

virtual_entity = SzEngineGetVirtualEntityByRecordIDResponse.from_json_data(json.loads(response))

print(
    f"RESOLVED_ENTITY.FEATURES['ID_KEY'][0].FEAT_DESC: {virtual_entity.resolved_entity.features['ID_KEY'][0].feat_desc}\n"
)

# Looping through list.

# bob = virtual_entity.resolved_entity.features.
addresses = virtual_entity.resolved_entity.features["ID_KEY"]
for address in addresses:
    print(f"    ID_KEY FEAT_DESC: {address.feat_desc}")

# -----------------------------------------------------------------------------
# Demonstrate reconstructed JSON.
# -----------------------------------------------------------------------------

print("\n--- Demonstrate reconstructed JSON --------------------------------------------\n")

json_dict = {
    "DATA_SOURCES": [
        {"DSRC_ID": 1, "DSRC_CODE": "TEST"},
        {"DSRC_ID": 2, "DSRC_CODE": "SEARCH"},
    ]
}
json_string = json.dumps(json_dict)

# Unmarshall JSON string into a object.

data_source_registry = SzConfigGetDataSourceRegistryResponse.from_json_data(json_dict)

# Show individual (ID, Code) pairs.

for data_source in data_source_registry.data_sources:
    print(f"                ID: {data_source.dsrc_id} Code: {data_source.dsrc_code}")

# Reconstruct JSON.

reconstructed_string = data_source_registry.to_json_data()

# Compare original and reconstructed JSON.

print(f"     Original JSON: {json_string}")
print(f"Reconstructed JSON: {reconstructed_string} - notice JSON keys have been sorted.")

# -----------------------------------------------------------------------------
# Show transformation from "from_json_data()" to "to_json_data"
# -----------------------------------------------------------------------------

print("\n---- Simple examples ----------------------------------------------------------\n")

# SzEngine add_record_with_info -----------------------------------------------

virtual_entity = SzEngineAddRecordResponse.from_json_data(json.loads(mock_szengine_add_record_with_info()))
print(
    f"SzEngineAddRecordResponse: DataSource: {virtual_entity.data_source}; RecordID: {virtual_entity.record_id}; Affected entity: {virtual_entity.affected_entities[0].entity_id}"
)

# SzEngine delete_record_with_info --------------------------------------------

virtual_entity = SzEngineDeleteRecordResponse.from_json_data(json.loads(mock_szengine_delete_record_with_info()))
print(
    f"SzEngineDeleteRecordResponse: DataSource: {virtual_entity.data_source}; RecordID: {virtual_entity.record_id}; Affected entity: {virtual_entity.affected_entities[0].entity_id}"
)

# SzEngine szengine_get_virtual_entity_by_record_id ------------------------------------

virtual_entity = SzEngineGetVirtualEntityByRecordIDResponse.from_json_data(
    json.loads(mock_szengine_get_virtual_entity_by_record_id(record_keys_parameter.to_json_data(), 0))
)
print(
    f"SzEngineGetVirtualEntityByRecordIDResponse: Simple  description: {virtual_entity.resolved_entity.features['NAME'][0].feat_desc}"
)

feature_list = virtual_entity.resolved_entity.features["NAME"]
for feature in feature_list:
    feat_desc_list = feature.feat_desc_values
    for feat_desc in feat_desc_list:
        print(f"SzEngineGetVirtualEntityByRecordIDResponse: Feature description: {feat_desc.feat_desc}")

# Compare the use of Python objects above with the following straight JSON parsing.
# - Issue: No static checking can be done on JSON keys
# - Issue: No editor hints
virtual_entity = json.loads(mock_szengine_get_virtual_entity_by_record_id(record_keys_parameter.to_json_data(), 0))
feature_list = virtual_entity.get("RESOLVED_ENTITY", {}).get("FEATURES", {}).get("NAME", [])
for feature in feature_list:
    feat_desc_list = feature.get("FEAT_DESC_VALUES")
    for feat_desc in feat_desc_list:
        print(f"SzEngineGetVirtualEntityByRecordIDResponse: Feature description: {feat_desc.get('FEAT_DESC')}")

# -----------------------------------------------------------------------------
# test area
# -----------------------------------------------------------------------------

print("\n---- Test area ----------------------------------------------------------------\n")

virtual_entity = SzConfigRegisterDataSourceResponse.from_json_data(
    file("SzConfigRegisterDataSourceResponse-test-001.json")
)
print_fmt(virtual_entity, "response.dsrc_id")


virtual_entity = SzConfigExportResponse.from_json_data(file("SzConfigExportResponse-test-001.json"))
print_fmt(virtual_entity, "response.g2_config.cfg_dfbom[0].dfcall_id")


virtual_entity = SzConfigGetDataSourceRegistryResponse.from_json_data(
    file("SzConfigGetDataSourceRegistryResponse-test-001.json")
)
print_fmt(virtual_entity, "response.data_sources[0].dsrc_id")


virtual_entity = SzConfigManagerGetConfigRegistryResponse.from_json_data(
    file("SzConfigManagerGetConfigRegistryResponse-test-001.json")
)
print_fmt(virtual_entity, "response.configs[0].config_id")


virtual_entity = SzDiagnosticCheckRepositoryPerformanceResponse.from_json_data(
    file("SzDiagnosticCheckRepositoryPerformanceResponse-test-001.json")
)
print_fmt(virtual_entity, "response.num_records_inserted")


virtual_entity = SzDiagnosticGetRepositoryInfoResponse.from_json_data(
    file("SzDiagnosticGetRepositoryInfoResponse-test-001.json")
)
print_fmt(virtual_entity, "response.data_stores[0].location")


virtual_entity = SzDiagnosticGetFeatureResponse.from_json_data(file("SzDiagnosticGetFeatureResponse-test-001.json"))
print_fmt(virtual_entity, "response.lib_feat_id")


virtual_entity = SzEngineAddRecordResponse.from_json_data(file("SzEngineAddRecordResponse-test-002.json"))
print_fmt(virtual_entity, "response.affected_entities[0].entity_id")


virtual_entity = SzEngineDeleteRecordResponse.from_json_data(file("SzEngineDeleteRecordResponse-test-002.json"))
print_fmt(virtual_entity, "response.affected_entities[0].entity_id")


# virtual_entity = SzEngineFetchNextResponse.from_json_data({})
# x = virtual_entity.value


virtual_entity = SzEngineFindInterestingEntitiesByRecordIDResponse.from_json_data(
    file("SzEngineFindInterestingEntitiesByRecordIdResponse-test-001.json")
)
print_fmt(
    virtual_entity,
    "response.interesting_entities",
)

virtual_entity = SzEngineFindNetworkByEntityIDResponse.from_json_data(
    file("SzEngineFindNetworkByEntityIdResponse-test-003.json")
)
print_fmt(
    virtual_entity,
    "response.entities[0].related_entities[0].entity_id",
)


virtual_entity = SzEngineFindNetworkByRecordIDResponse.from_json_data(
    file("SzEngineFindNetworkByRecordIdResponse-test-003.json")
)
print_fmt(
    virtual_entity,
    "response.entities[0].related_entities[0].entity_id",
)


virtual_entity = SzEngineFindPathByEntityIDResponse.from_json_data(
    file("SzEngineFindPathByEntityIdResponse-test-001.json")
)
print_fmt(
    virtual_entity,
    "response.entities[0].resolved_entity.entity_id",
)


virtual_entity = SzEngineFindPathByRecordIDResponse.from_json_data(
    file("SzEngineFindPathByRecordIdResponse-test-001.json")
)
print_fmt(
    virtual_entity,
    "response.entities[0].resolved_entity.entity_id",
)


virtual_entity = SzEngineGetEntityByEntityIDResponse.from_json_data({})
virtual_entity = SzEngineGetEntityByRecordIDResponse.from_json_data({})
virtual_entity = SzEngineGetRecordResponse.from_json_data({})
virtual_entity = SzEngineGetRedoRecordResponse.from_json_data({})
virtual_entity = SzEngineGetVirtualEntityByRecordIDResponse.from_json_data({})
virtual_entity = SzEngineHowEntityByEntityIDResponse.from_json_data({})
virtual_entity = SzEngineProcessRedoRecordResponse.from_json_data({})
virtual_entity = SzEngineReevaluateEntityResponse.from_json_data({})
virtual_entity = SzEngineReevaluateRecordResponse.from_json_data({})
virtual_entity = SzEngineSearchByAttributesResponse.from_json_data({})
virtual_entity = SzEngineWhyEntitiesResponse.from_json_data({})
virtual_entity = SzEngineWhyRecordInEntityResponse.from_json_data({})
virtual_entity = SzEngineWhyRecordsResponse.from_json_data({})
virtual_entity = SzProductGetLicenseResponse.from_json_data({})
virtual_entity = SzProductGetVersionResponse.from_json_data({})


# response = SzEngineGetEntityByEntityIDResponse.from_json_data({})
# x = response.resolved_entity

# response = SzEngineFindNetworkByEntityIDResponse.from_json_data({})
# x = response.entities[0].related_entities[0].record_summary[0]

# response = SzConfigManagerGetConfigRegistryResponse.from_json_data({})
# x = response.configs[0].


# response = SzProductLicenseResponse.from_json_data({})
# response.

# response = SzEngineGetEntityByEntityIDResponse.from_json_data({})
# x = response.resolved_entity.entity_id
