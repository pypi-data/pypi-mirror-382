/*
Module sz-sdk-jackson-type-definition has input/output types for Senzing API SDKs.
*/
package main

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/senzing-garage/go-helpers/settings"
	"github.com/senzing-garage/sz-sdk-go-core/szabstractfactory"
	"github.com/senzing-garage/sz-sdk-go/senzing"
	"github.com/senzing-garage/sz-sdk-json-type-definition/go/typedef"
)

const (
	instanceName   = "SzEngine Test"
	verboseLogging = senzing.SzNoLogging
)

func main() {
	var err error

	ctx := context.Background()

	// ------------------------------------------------------------------------
	// Create Senzing objects.
	// ------------------------------------------------------------------------

	szAbstractFactory := createSzAbstractFactory(ctx)
	szEngine, err := szAbstractFactory.CreateEngine(ctx)
	panicOnError(err)
	szConfigManager, err := szAbstractFactory.CreateConfigManager(ctx)
	panicOnError(err)

	// ------------------------------------------------------------------------
	// Create Senzing objects.
	// ------------------------------------------------------------------------

	// testStruct1 := typedef.SzEngineGetEntityByEntityIDResponse{}
	// x := testStruct1.ResolvedEntity.FeatureIds[0].UsageType

	// testStruct2 := typedef.SzEngineWhyEntitiesResponse{}
	// y := testStruct2.WhyResults[0].MatchInfo.WhyKey

	// testStruct3 := typedef.SzEngineGetRecordResponse{}
	// z := testStruct3.JSONData["bob"]

	// ------------------------------------------------------------------------
	// Demonstrate creating input parameter and parsing output result.
	// ------------------------------------------------------------------------

	outputf("--- Demonstrate creating input parameter and parsing output result ------------\n\n")

	// Example of creating a JSON input parameter.
	// The advantage is that this is checked at compilation time.

	recordKeysStruct := typedef.SzEngineGetVirtualEntityByRecordIDRecordKeys{
		Records: []typedef.RecordKey{
			{
				DataSource: "CUSTOMERS",
				RecordID:   "1001",
			},
			{
				DataSource: "REFERENCE",
				RecordID:   "2141",
			},
		},
	}

	recordKeysBytes, err := json.Marshal(recordKeysStruct)
	panicOnError(err)

	// Call Senzing SDK.

	response, err := szEngine.GetVirtualEntityByRecordID(
		ctx,
		string(recordKeysBytes),
		senzing.SzVirtualEntityDefaultFlags,
	)
	panicOnError(err)

	// Parse response.

	virtualEntity := typedef.SzEngineGetVirtualEntityByRecordIDResponse{}
	if err := json.Unmarshal([]byte(response), &virtualEntity); err != nil {
		panic(err)
	}

	outputf(
		"RESOLVED_ENTITY.FEATURES['ADDRESS'][0].FEAT_DESC: %s\n\n",
		virtualEntity.ResolvedEntity.Features["ADDRESS"][0].FeatDesc,
	)

	// Looping through list.

	addresses := virtualEntity.ResolvedEntity.Features["ADDRESS"]
	for _, address := range addresses {
		addressBytes, err := json.Marshal(address)
		panicOnError(err)

		addressStruct := typedef.FeatureForAttributes{}

		if err = json.Unmarshal(addressBytes, &addressStruct); err != nil {
			panic(err)
		}

		outputln("   ADDRESS FEAT_DESC:", addressStruct.FeatDesc)
	}

	// ------------------------------------------------------------------------
	// Demonstrate reconstructed JSON.
	// ------------------------------------------------------------------------

	activeConfigID, err := szEngine.GetActiveConfigID(ctx)
	panicOnError(err)
	szConfig, err := szConfigManager.CreateConfigFromConfigID(ctx, activeConfigID)
	panicOnError(err)

	dataSourceRegistry, err := szConfig.GetDataSourceRegistry(ctx)
	panicOnError(err)

	outputf("\n--- Demonstrate reconstructed JSON --------------------------------------------\n\n")
	// jsonString := `{"DATA_SOURCES":[{"DSRC_ID":1,"DSRC_CODE":"TEST"},{"DSRC_ID":2,"DSRC_CODE":"SEARCH"}]}`

	// Unmarshall JSON string into a structure.

	jsonStruct := typedef.SzConfigGetDataSourceRegistryResponse{}
	if err = json.Unmarshal([]byte(dataSourceRegistry), &jsonStruct); err != nil {
		panic(err)
	}

	// Show individual (ID, Code) pairs.

	for _, datasource := range jsonStruct.DataSources {
		outputf("                ID: %d  Code: %s\n", datasource.DsrcID, datasource.DsrcCode)
	}

	// Reconstruct JSON.

	reconstructedString, err := json.Marshal(jsonStruct)
	panicOnError(err)

	// Compare original and reconstructed JSON.

	outputf("     Original JSON: %s\n", dataSourceRegistry)
	outputf("Reconstructed JSON: %s - notice JSON keys have been sorted.\n",
		string(reconstructedString))
}

// ----------------------------------------------------------------------------
// Helper functions
// ----------------------------------------------------------------------------

func panicOnError(err error) {
	if err != nil {
		panic(err)
	}
}

func createSzAbstractFactory(ctx context.Context) senzing.SzAbstractFactory {
	var result senzing.SzAbstractFactory

	_ = ctx

	// Create Senzing engine configuration JSON.

	settings, err := settings.BuildSimpleSettingsUsingEnvVars()
	panicOnError(err)

	result = &szabstractfactory.Szabstractfactory{
		ConfigID:       senzing.SzInitializeWithDefaultConfiguration,
		InstanceName:   instanceName,
		Settings:       settings,
		VerboseLogging: verboseLogging,
	}

	return result
}

func outputln(message ...any) {
	fmt.Println(message...) //nolint
}

func outputf(format string, message ...any) {
	fmt.Printf(format, message...) //nolint
}

// func pathToTestdata(filename string) string {
// 	return "./testdata/" + filename
// }

// func mockSzEngineGetVirtualEntityByRecordID(ctx context.Context, recordKeys string, flags int64) (string, error) {
// 	_ = ctx
// 	_ = flags

// 	outputf("recordKeys Parameter: %s\n\n", recordKeys)

// 	filePath := pathToTestdata("SzEngineGetVirtualEntityByRecordIdResponse-test-001.json")
// 	result, err := os.ReadFile(filePath)

// 	return string(result), err
// }
