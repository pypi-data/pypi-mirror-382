
import * as fs from 'fs';


import {
    SzEngineGetVirtualEntityByRecordIdRecordKeys,
    SzEngineGetVirtualEntityByRecordIdResponse,
    SzConfigGetDataSourceRegistryResponse
} from './typescript/index';

// ----------------------------------------------------------------------------
// Demonstrate creating input parameter and parsing output result.
// ----------------------------------------------------------------------------

console.log("--- Demonstrate creating input parameter and parsing output result ------------\n")

// Example of creating a JSON input parameter.
// The advantage is that this is checked at compilation time.

let recordKeysDict = {
    "RECORDS": [
        { "DATA_SOURCE": "DATA_SOURCE_1", "RECORD_ID": "RECORD_ID_1" },
        { "DATA_SOURCE": "DATA_SOURCE_2", "RECORD_ID": "RECORD_ID_2" },
    ]
}

let recordKey: SzEngineGetVirtualEntityByRecordIdRecordKeys = recordKeysDict

// Simulate calling Senzing SDK.

let virtualEntityJson = mockSzEngineGetVirtualEntityByRecordID(JSON.stringify(recordKey))

// Parse response.

let virtualEntity: SzEngineGetVirtualEntityByRecordIdResponse = JSON.parse(virtualEntityJson) as SzEngineGetVirtualEntityByRecordIdResponse
console.log(
    "RESOLVED_ENTITY.FEATURES['ID_KEY'][0].FEAT_DESC: %s\n",
    virtualEntity.RESOLVED_ENTITY.FEATURES["ID_KEY"][0].FEAT_DESC,
)

// Looping through list.

for (const address of virtualEntity.RESOLVED_ENTITY.FEATURES["ID_KEY"]) {
    console.log("    ID_KEY FEAT_DESC:", address.FEAT_DESC)
}

// ----------------------------------------------------------------------------
// Demonstrate reconstructed JSON.
// ----------------------------------------------------------------------------

console.log("\n--- Demonstrate reconstructed JSON --------------------------------------------\n")
let jsonString: string = "{\"DATA_SOURCES\":[{\"DSRC_ID\":1,\"DSRC_CODE\":\"TEST\"},{\"DSRC_ID\":2,\"DSRC_CODE\":\"SEARCH\"}]}";

// Unmarshall JSON string into a structure.

let dataSourceRegistry: SzConfigGetDataSourceRegistryResponse = JSON.parse(jsonString) as SzConfigGetDataSourceRegistryResponse

// Show individual (ID, Code) pairs.

for (const datasource of dataSourceRegistry.DATA_SOURCES) {
    console.log(`                ID: ${datasource.DSRC_ID} CODE: ${datasource.DSRC_CODE}`)
}

// Reconstruct JSON.

let reconstructedString: string = JSON.stringify(dataSourceRegistry);

// Compare original and reconstructed JSON.

console.log(`     Original JSON: ${jsonString}`);
console.log(`Reconstructed JSON: ${reconstructedString}\n`,);

// ----------------------------------------------------------------------------
// Helper functions
// ----------------------------------------------------------------------------

function mockSzEngineGetVirtualEntityByRecordID(recordKeys: string): string {
    console.log(`recordKeys Parameters ${recordKeys}\n`)
    return fs.readFileSync('./testdata/responses_generated/SzEngineGetVirtualEntityByRecordIdResponse-test-015.json', 'utf-8');
}