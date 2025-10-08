// # For more information, visit https://jsontypedef.com/docs/java-codegen/

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.senzing.typedef.DataSource;
import com.senzing.typedef.FeatureForAttributes;
import com.senzing.typedef.RecordKey;
import com.senzing.typedef.RecordKeys;
import com.senzing.typedef.SzConfigGetDataSourceRegistryResponse;
import com.senzing.typedef.SzEngineGetVirtualEntityByRecordIdResponse;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

class Main {

    public static void main(String[] args) throws Exception {

        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.registerModule(new JavaTimeModule());

        // --------------------------------------------------------------------
        // Demonstrate creating input parameter and parsing output result.
        // --------------------------------------------------------------------

        System.out.printf("\n--- Demonstrate creating input parameter and parsing output result ------------\n\n");

        // Simulate calling Senzing SDK.

        RecordKeys recordKeys = new RecordKeys();
        List<RecordKey> recordKeyList = new ArrayList<>();

        RecordKey recordKey1 = new RecordKey();
        recordKey1.setDataSource("DATA_SOURCE_1");
        recordKey1.setRecordId("RECORD_ID_1");
        recordKeyList.add(recordKey1);

        RecordKey recordKey2 = new RecordKey();
        recordKey2.setDataSource("DATA_SOURCE_2");
        recordKey2.setRecordId("RECORD_ID_2");
        recordKeyList.add(recordKey2);

        recordKeys.setRecords(recordKeyList);
        String recordKeysJson;
        try {
            recordKeysJson = objectMapper.writeValueAsString(recordKeys);
        } catch (Exception e) {
            throw e;
        }

        // Simulate calling Senzing SDK.

        String response = mockSzEngineGetVirtualEntityByRecordId(recordKeysJson, 1);

        // Parse response.

        SzEngineGetVirtualEntityByRecordIdResponse virtualEntity;
        try {
            virtualEntity = objectMapper.readValue(response, SzEngineGetVirtualEntityByRecordIdResponse.class);
        } catch (Exception e) {
            throw e;
        }

        // Integer example = virtualEntity.getResolvedEntity().getEntityId();

        System.out.printf("RESOLVED_ENTITY.FEATURES['ID_KEY'][0].FEAT_DESC: %s\n\n",
                virtualEntity.getResolvedEntity().getFeatures().get("ID_KEY").get(0).getFeatDesc());

        // Looping through list.

        for (FeatureForAttributes feature : virtualEntity.getResolvedEntity().getFeatures().get("ID_KEY")) {
            System.out.printf("   ID_KEY FEAT_DESC: %s\n", feature.getFeatDesc());
        }

        // --------------------------------------------------------------------
        // Demonstrate reconstructed JSON.
        // --------------------------------------------------------------------

        System.out.printf("\n--- Demonstrate reconstructed JSON --------------------------------------------\n\n");

        String jsonString = "{\"DATA_SOURCES\":[{\"DSRC_ID\":1,\"DSRC_CODE\":\"TEST\"},{\"DSRC_ID\":2,\"DSRC_CODE\":\"SEARCH\"}]}";

        // Unmarshall JSON string into a object.

        SzConfigGetDataSourceRegistryResponse jsonStruct;
        try {
            jsonStruct = objectMapper.readValue(jsonString, SzConfigGetDataSourceRegistryResponse.class);
        } catch (Exception e) {
            throw e;
        }

        // Show individual (ID, Code) pairs.

        for (DataSource dataSource : jsonStruct.getDataSources()) {
            System.out.printf("                ID: %s  Code: %s\n", dataSource.getDsrcId(), dataSource.getDsrcCode());
        }

        // Reconstruct JSON.

        String reconstructedString = objectMapper.writeValueAsString(jsonStruct);

        // Compare original and reconstructed JSON.

        System.out.printf("     Original JSON: %s\n", jsonString);
        System.out.printf("Reconstructed JSON: %s - notice JSON keys have been sorted.\n", reconstructedString);

    }

    public static String mockSzEngineGetVirtualEntityByRecordId(String recordKeys, int flags) {
        String result = "";

        if (flags > 0) {
            System.out.printf("recordKeys Parameter: %s\n\n", recordKeys);
        }

        Path currentPath = Paths.get("").toAbsolutePath();
        String filePath = currentPath
                + "/testdata/responses_generated/SzEngineGetVirtualEntityByRecordIdResponse-test-015.json";
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                result += line;
            }
        } catch (IOException e) {
            System.err.println("Error reading file: " + e.getMessage());
        }

        return result;
    }

}