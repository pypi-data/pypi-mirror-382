// See https://aka.ms/new-console-template for more information

using Senzing.Typedef;
using System.Text.Json;


namespace Bob

{
    internal class Program
    {
        static void Main(string[] args)
        {
            Program myProgram = new Program();

            // ----------------------------------------------------------------
            // Demonstrate creating input parameter and parsing output result.
            // ----------------------------------------------------------------

            Console.WriteLine("--- Demonstrate creating input parameter and parsing output result ------------\n");

            // Example of creating a JSON input parameter.
            // The advantage is that this is checked at compilation time.

            IList<RecordKey> recordKeyList = new List<RecordKey>();

            RecordKey recordKey1 = new RecordKey
            {
                DataSource = "DATA_SOURCE_1",
                RecordId = "RECORD_ID_1"
            };
            recordKeyList.Add(recordKey1);

            RecordKey recordKey2 = new RecordKey
            {
                DataSource = "DATA_SOURCE_2",
                RecordId = "RECORD_ID_2"
            };
            recordKeyList.Add(recordKey2);

            SzEngineGetVirtualEntityByRecordIdRecordKeys recordKeyStruct = new SzEngineGetVirtualEntityByRecordIdRecordKeys
            {
                Records = recordKeyList
            };

            string recordKeysJson = JsonSerializer.Serialize(recordKeyStruct);

            // Simulate calling Senzing SDK.

            string response = myProgram.mockSzEngineGetVirtualEntityByRecordID(recordKeysJson, 1);

            // Parse response.

            SzEngineGetVirtualEntityByRecordIdResponse? virtualEntity = JsonSerializer.Deserialize<SzEngineGetVirtualEntityByRecordIdResponse>(response);
            if (virtualEntity != null)
            {
                Console.WriteLine("RESOLVED_ENTITY.FEATURES['ID_KEY'][0].FEAT_DESC: {0:G}\n",
                    virtualEntity.ResolvedEntity.Features["ID_KEY"][0].FeatDesc);

                // Looping through list.

                IList<FeatureForAttributes> addresses = virtualEntity.ResolvedEntity.Features["ID_KEY"];
                foreach (FeatureForAttributes address in addresses)
                {
                    Console.WriteLine("    ID_KEY FEAT_DESC: {0:G}", address.FeatDesc);
                }
            }

            // ----------------------------------------------------------------
            // Demonstrate reconstructed JSON.
            // ----------------------------------------------------------------

            Console.WriteLine("\n--- Demonstrate reconstructed JSON --------------------------------------------\n");
            string jsonString = "{\"DATA_SOURCES\":[{\"DSRC_ID\":1,\"DSRC_CODE\":\"TEST\"},{\"DSRC_ID\":2,\"DSRC_CODE\":\"SEARCH\"}]}";

            // Unmarshall JSON string into a structure.

            SzConfigGetDataSourceRegistryResponse? dataSourceRegistry = JsonSerializer.Deserialize<SzConfigGetDataSourceRegistryResponse>(jsonString);

            // Show individual (ID, Code) pairs.

            if (dataSourceRegistry != null)
            {
                foreach (DataSource datasource in dataSourceRegistry.DataSources)
                {
                    Console.WriteLine("                ID: {0:G}  Code: {1:G}", datasource.DsrcId, datasource.DsrcCode);
                }
            }

            // Reconstruct JSON.

            string reconstructedString = JsonSerializer.Serialize(dataSourceRegistry);

            // Compare original and reconstructed JSON.

            Console.WriteLine("     Original JSON: {0:G}", jsonString);
            Console.WriteLine("Reconstructed JSON: {0:G} - notice JSON keys have been sorted.\n", reconstructedString);

        }

        public string mockSzEngineGetVirtualEntityByRecordID(string recordKeys, int flags)
        {
            if (flags > 0)
            {
                Console.WriteLine("recordKeys Parameter: {0:G}\n", recordKeys);
            }

            string currentPath = Directory.GetCurrentDirectory();
            string filePath = currentPath + "/testdata/responses_generated/SzEngineGetVirtualEntityByRecordIdResponse-test-015.json";

            string result = "";
            StreamReader file = new StreamReader(filePath);

            try
            {
                string? line = file.ReadLine();
                while (line != null)
                {
                    result += line;
                    line = file.ReadLine();
                }
            }
            catch (Exception e)
            {
                Console.WriteLine("Exception: " + e.Message);
            }
            finally
            {
                file.Close();
            }

            return result;
        }

    }
}
