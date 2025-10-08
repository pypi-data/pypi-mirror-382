package typedef_test

import (
	"bufio"
	"context"
	"encoding/json"
	"io/fs"
	"os"
	"path"
	"testing"

	"github.com/senzing-garage/sz-sdk-json-type-definition/go/typedef"
	"github.com/stretchr/testify/assert"
)

const (
	testDataPath = "../../testdata/responses_senzing"
)

func testError(ctx context.Context, t *testing.T, err error) {
	t.Helper()

	_ = ctx

	if err != nil {
		t.Log("Error:", err.Error())
		assert.FailNow(t, err.Error())
	}
}

// ----------------------------------------------------------------------------
// --- Test cases
// ----------------------------------------------------------------------------

func TestSz(test *testing.T) {
	ctx := context.TODO()
	root := os.DirFS(testDataPath)

	testCases := []struct {
		name      string
		theStruct any
	}{
		{
			name:      "SzConfigExportResponse*.jsonl",
			theStruct: typedef.SzConfigExportResponse{},
		},
		{
			name:      "SzConfigGetDataSourceRegistryResponse*.jsonl",
			theStruct: typedef.SzConfigGetDataSourceRegistryResponse{},
		},
		{
			name:      "SzConfigManagerGetConfigRegistryResponse*.jsonl",
			theStruct: typedef.SzConfigManagerGetConfigRegistryResponse{},
		},
		{
			name:      "SzConfigRegisterDataSourceResponse*.jsonl",
			theStruct: typedef.SzConfigRegisterDataSourceResponse{},
		},

		{
			name:      "SzDiagnosticCheckRepositoryPerformanceResponse*.jsonl",
			theStruct: typedef.SzDiagnosticCheckRepositoryPerformanceResponse{},
		},
		{
			name:      "SzDiagnosticGetFeatureResponse*.jsonl",
			theStruct: typedef.SzDiagnosticGetFeatureResponse{},
		},
		{
			name:      "SzEngineDeleteRecordResponse*.jsonl",
			theStruct: typedef.SzEngineDeleteRecordResponse{},
		},
		{
			name:      "SzEngineFindInterestingEntitiesByEntityIdResponse*.jsonl",
			theStruct: typedef.SzEngineFindInterestingEntitiesByEntityIDResponse{},
		},
		{
			name:      "SzEngineFindInterestingEntitiesByRecordIdResponse*.jsonl",
			theStruct: typedef.SzEngineFindInterestingEntitiesByRecordIDResponse{},
		},
		{
			name:      "SzEngineFindNetworkByEntityIdResponse*.jsonl",
			theStruct: typedef.SzEngineFindNetworkByEntityIDResponse{},
		},
		{
			name:      "SzEngineFindNetworkByRecordIdResponse*.jsonl",
			theStruct: typedef.SzEngineFindNetworkByRecordIDResponse{},
		},
		{
			name:      "SzEngineFindPathByEntityIdResponse*.jsonl",
			theStruct: typedef.SzEngineFindPathByEntityIDResponse{},
		},
		{
			name:      "SzEngineFindPathByRecordIdResponse*.jsonl",
			theStruct: typedef.SzEngineFindPathByRecordIDResponse{},
		},
		{
			name:      "SzEngineGetEntityByEntityIdResponse*.jsonl",
			theStruct: typedef.SzEngineGetEntityByEntityIDResponse{},
		},
		{
			name:      "SzEngineGetEntityByRecordIdResponse*.jsonl",
			theStruct: typedef.SzEngineGetEntityByRecordIDResponse{},
		},
		{
			name:      "SzEngineGetRecordResponse*.jsonl",
			theStruct: typedef.SzEngineGetRecordResponse{},
		},
		{
			name:      "SzEngineGetRecordPreviewResponse*.jsonl",
			theStruct: typedef.SzEngineGetRecordPreviewResponse{},
		},
		{
			name:      "SzEngineGetVirtualEntityByRecordIdResponse*.jsonl",
			theStruct: typedef.SzEngineGetVirtualEntityByRecordIDResponse{},
		},
		{
			name:      "SzEngineHowEntityByEntityIdResponse*.jsonl",
			theStruct: typedef.SzEngineHowEntityByEntityIDResponse{},
		},
		{
			name:      "SzEngineGetRedoRecordResponse*.jsonl",
			theStruct: typedef.SzEngineGetRedoRecordResponse{},
		},
		{
			name:      "SzEngineProcessRedoRecordResponse*.jsonl",
			theStruct: typedef.SzEngineProcessRedoRecordResponse{},
		},
		{
			name:      "SzEngineReevaluateEntityResponse*.jsonl",
			theStruct: typedef.SzEngineReevaluateEntityResponse{},
		},
		{
			name:      "SzEngineReevaluateRecordResponse*.jsonl",
			theStruct: typedef.SzEngineReevaluateRecordResponse{},
		},
		{
			name:      "SzEngineSearchByAttributesResponse*.jsonl",
			theStruct: typedef.SzEngineSearchByAttributesResponse{},
		},
		{
			name:      "SzDiagnosticGetRepositoryInfoResponse*.jsonl",
			theStruct: typedef.SzDiagnosticGetRepositoryInfoResponse{},
		},
		{
			name:      "SzEngineGetStatsResponse*.jsonl",
			theStruct: typedef.SzEngineGetStatsResponse{},
		},
		{
			name:      "SzProductGetLicenseResponse*.jsonl",
			theStruct: typedef.SzProductGetLicenseResponse{},
		},
		{
			name:      "SzProductGetVersionResponse*.jsonl",
			theStruct: typedef.SzProductGetVersionResponse{},
		},
	}

	for _, testCase := range testCases {
		test.Run(testCase.name, func(test *testing.T) {
			jsonStruct := testCase.theStruct

			entries, err := fs.Glob(root, testCase.name)
			testError(ctx, test, err)

			for _, entry := range entries {
				testFile := path.Join(testDataPath, entry)
				file, err := os.Open(testFile)
				testError(ctx, test, err)

				defer file.Close()

				scanner := bufio.NewScanner(file)
				for scanner.Scan() {
					line := scanner.Text()
					if len(line) > 0 {
						err = json.Unmarshal([]byte(line), &jsonStruct)
						testError(ctx, test, err)
						_, err = json.Marshal(jsonStruct)
						testError(ctx, test, err)
					}
				}
			}
		})
	}
}
