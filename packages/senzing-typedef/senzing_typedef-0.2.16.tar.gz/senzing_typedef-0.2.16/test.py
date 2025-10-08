#! /usr/bin/env python3

# pylint: disable=duplicate-code

"""
For more information, visit https://jsontypedef.com/docs/python-codegen/
"""

import os
import pathlib

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------


def path_to_testdata(filename: str) -> str:
    """Determine the path to the test data."""
    current_path = pathlib.Path(__file__).parent.resolve()
    result = os.path.abspath(f"{current_path}/testdata/{filename}")
    return result


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


def test_szengine_find_network_by_record_id_001():
    """Test sz_engine.find_network_by_record_id()"""


# def test_szengine_find_network_by_record_id_001():
#     with open(
#         path_to_testdata("SzEngineFindNetworkByRecordIdResponse-test-001.json"),
#         encoding="utf-8",
#     ) as input_file:
#         response = SzEngineFindNetworkByRecordIDResponse.from_json_data(
#             json.load(input_file)
#         )
#     assert response.entity_paths == []
#     assert response.entities[0].resolved_entity.entity_id == 1
#     assert response.entities[0].resolved_entity.entity_name == "Robert Smith"
#     assert (
#         response.entities[0].resolved_entity.record_summary[0].data_source
#         == "CUSTOMERS"
#     )


# def test_szengine_find_path_by_entity_id_001():
#     with open(
#         path_to_testdata("SzEngineFindPathByEntityIdResponse-test-001.json"),
#         encoding="utf-8",
#     ) as input_file:
#         response = SzEngineFindPathByEntityIDResponse.from_json_data(
#             json.load(input_file)
#         )
#     assert response.entity_paths[0].start_entity_id == 1
#     assert response.entities[0].related_entities == []
#     assert response.entities[0].resolved_entity.entity_id == 1
#     assert response.entities[0].resolved_entity.entity_name == "Robert Smith"
#     assert response.entities[0].resolved_entity.record_summary[0].record_count == 3


# def test_szengine_find_path_by_record_id_001():
#     with open(
#         path_to_testdata("SzEngineFindPathByRecordIdResponse-test-001.json"),
#         encoding="utf-8",
#     ) as input_file:
#         response = SzEngineFindPathByRecordIDResponse.from_json_data(
#             json.load(input_file)
#         )
#     assert response.entity_paths[0].start_entity_id == 1
#     assert response.entities[0].related_entities == []
#     assert response.entities[0].resolved_entity.entity_id == 1
#     assert response.entities[0].resolved_entity.entity_name == "Robert Smith"
#     assert response.entities[0].resolved_entity.record_summary[0].record_count == 3


# def test_szengine_get_entity_by_entity_id_01():
#     with open(
#         path_to_testdata("SzEngineGetEntityByEntityIdResponse-test-001.json"),
#         encoding="utf-8",
#     ) as input_file:
#         response = SzEngineGetEntityByEntityIDResponse.from_json_data(
#             json.load(input_file)
#         )
#     assert response.related_entities == []
#     assert response.resolved_entity.entity_id == 1
#     assert response.resolved_entity.entity_name == "Robert Smith"
#     feature_json = response.resolved_entity.features["ADDRESS"][0].feat_desc
#     feature = FeatureForAttribute.from_json_data(feature_json)
#     assert feature.feat_desc == "1515 Adela Lane Las Vegas NV 89111"
#     assert feature.feat_desc_values[0].lib_feat_id == 20


# def test_szengine_get_entity_by_entity_id_001():
#     with open(
#         path_to_testdata("SzEngineGetEntityByEntityIdResponse-test-001.json"),
#         encoding="utf-8",
#     ) as input_file:
#         response = SzEngineGetEntityByEntityIDResponse.from_json_data(
#             json.load(input_file)
#         )
#     assert response.related_entities == []
#     assert response.resolved_entity.entity_id == 1
#     assert response.resolved_entity.entity_name == "Robert Smith"
#     assert (
#         response.resolved_entity.features["ADDRESS"][0].feat_desc
#         == "1515 Adela Lane Las Vegas NV 89111"
#     )
#     assert response.resolved_entity.features["ADDRESS"][0].lib_feat_id == 20


# def test_szengine_get_entity_by_entity_id_003():
#     with open(
#         path_to_testdata("SzEngineGetEntityByEntityIdResponse-test-003.json"),
#         encoding="utf-8",
#     ) as input_file:
#         response = SzEngineGetEntityByEntityIDResponse.from_json_data(
#             json.load(input_file)
#         )
#     assert response.related_entities == []
#     assert response.resolved_entity.entity_id == 1
#     assert response.resolved_entity.entity_name == "blank"
#     assert response.resolved_entity.features["ADDRESS"][0].feat_desc == "blank"
#     assert (
#         response.resolved_entity.features["ADDRESS"][0].feat_desc_values[0].lib_feat_id
#         == 1
#     )


# def test_szengine_get_entity_by_record_id_001():
#     with open(
#         path_to_testdata("SzEngineGetEntityByRecordIdResponse-test-001.json"),
#         encoding="utf-8",
#     ) as input_file:
#         response = SzEngineGetEntityByRecordIDResponse.from_json_data(
#             json.load(input_file)
#         )
#     assert response.related_entities == []
#     assert response.resolved_entity.entity_id == 1
#     assert response.resolved_entity.entity_name == "Robert Smith"
#     assert (
#         response.resolved_entity.features["ADDRESS"][0].feat_desc
#         == "1515 Adela Lane Las Vegas NV 89111"
#     )
#     assert (
#         response.resolved_entity.features["ADDRESS"][0].feat_desc_values[0].lib_feat_id
#         == 20
#     )


# def test_szengine_get_record_003():
#     with open(
#         path_to_testdata("SzEngineGetRecordResponse-test-003.json"), encoding="utf-8"
#     ) as input_file:
#         response = SzEngineGetRecordResponse.from_json_data(json.load(input_file))
#     assert response.data_source == "CUSTOMERS"
#     assert response.record_id == "1001"
#     assert isinstance(response.json_data, dict)
#     assert response.json_data["DATA_SOURCE"] == "CUSTOMERS"
#     assert response.json_data["RECORD_ID"] == "1001"


# TODO: Fix this
# def test_szengine_get_redo_record_014():
#     with open(
#         path_to_testdata("SzEngineGetRedoRecordResponse-test-001.json"),
#         encoding="utf-8",
#     ) as input_file:
#         response = SzEngineGetRedoRecordResponse.from_json_data(json.load(input_file))
#     assert response.value == {}


# def test_szengine_get_virtual_entity_by_record_id_001():
#     with open(
#         path_to_testdata("SzEngineGetVirtualEntityByRecordIdResponse-test-001.json"),
#         encoding="utf-8",
#     ) as input_file:
#         response = SzEngineGetVirtualEntityByRecordIDResponse.from_json_data(
#             json.load(input_file)
#         )
#     assert response.resolved_entity.entity_id == 1
#     assert response.resolved_entity.entity_name == "Robert Smith"
#     assert response.resolved_entity.features["NAME"][0].feat_desc == "Robert Smith"
#     assert response.resolved_entity.features["NAME"][0].lib_feat_id == 1
#     assert (
#         response.resolved_entity.features["NAME"][0].feat_desc_values[1].lib_feat_id
#         == 18
#     )


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # test_szengine_add_record_with_info_005()
    pass
