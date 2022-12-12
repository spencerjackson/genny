class CollectionDescription:
  def __init__(self, name, description, size):
    self.name = name
    self.description = description
    self.size = size

collections = {
  "vlf": CollectionDescription("vlf", "All field/value pairs have very low frequency", 100000),
  "mlf": CollectionDescription("mlf", "All field/value pairs have medium low frequency", 100000),
  "lf": CollectionDescription("lf", "All field/value pairs have low frequency", 100000),
  "hf": CollectionDescription("hf", "All field/value pairs have high frequency", 100000),
  "mhf": CollectionDescription("mhf", "All field/value pairs have medium high frequency", 100000),
  "vhf": CollectionDescription("vhf", "All field/value pairs have very highfrequency", 100000),
  "blimit": CollectionDescription("blimit", "All field/value pairs have sane frequency", 1000000),
  "pbl": CollectionDescription("pbl", "All fields have values distributed as per the power-law with an added constraint that each field should have at least one value with frequencies in the following ranges: [1, 10], (10, 100], (100, 1k], (1k, 10k], (10k, 50k], (50k, 100k]", 100000),
}

numEncryptedFields = [0,1,5,10]
contentionFactors = [1,4,8,16]
clientThreadCounts = [4,8,16]

print("InsOnly Experiments")
for (name, coll) in collections.items():
  for enc in numEncryptedFields:
    for cf in contentionFactors:
      for tc in clientThreadCounts:
        testName = f"InsOnly-{coll.name}-{enc}-{cf}-{tc}"
        iterationsPerThread = coll.size / tc
        def generateFieldDescription():
            fieldDescription = ""
            for num in range(0, enc):
                if num is 0:
                  fieldDescription += "    QueryableEncryptedFields:\n"
                  fieldDescription += f'      field{num}: &field_schema {{ type: "long", queries: [{{queryType: "equality", contention: {cf}}}] }}\n'
                  continue
                else:
                  fieldDescription += f'      field{num}: *field_schema\n'
            return fieldDescription

        def generateAutoRun():
            if name is "blimit" and enc is 5 and cf is 4 and tc is 4:
              return """AutoRun:
- When:
    mongodb_setup:
      $eq:
      - single-replica-fle
    branch_name:
      $neq:
      - v4.0
      - v4.2
      - v4.4
      - v5.0
      - v6.0
      - v6.1
      - v6.2"""
            else:
              return ""

        with open(f"data/{testName}.yml", 'w+') as testFile:
          testFile.write(f"""SchemaVersion: 2018-07-01
Owner: "@10gen/server-security"
Description: |
  Performs a series of insert operations, using the following properties:
    - All documents have 11 fields, including 1 _id field, and 10 data fields.
    - The first {enc} data fields are encrypted.
    - _id is always unique.
    - Values in data fields fit a '{name}' distribution. {coll.description}.
    - The insertions are performed by {tc} client threads.
  This test is uniquely identified as '{testName}'.

Encryption:
  UseCryptSharedLib: true
  CryptSharedLibPath: /data/workdir/mongocrypt/lib/mongo_crypt_v1.so
  EncryptedCollections:
  - Database: genny_qebench
    Collection: testcoll
    EncryptionType: queryable
{generateFieldDescription()}

Clients:
  EncryptedPool:
    QueryOptions:
      maxPoolSize: 400
    EncryptionOptions:
      KeyVaultDatabase: "keyvault"
      KeyVaultCollection: "datakeys"
      EncryptedCollections:
      - genny_qebench.testcoll

LoadPhase: &load_phase
  Repeat: {iterationsPerThread}
  Collection: &collection_param {{^Parameter: {{Name: "Collection", Default: "testcoll"}}}}
  MetricsName: "load"
  Operations:
  - OperationName: insertOne
    OperationMetricsName: inserts
    OperationCommand:
      Document:
        field0: &valueFormat {{^RandomInt: {{min: 0, max: 100000, distribution: uniform}}}}
        field1: *valueFormat
        field2: *valueFormat
        field3: *valueFormat
        field4: *valueFormat
        field5: *valueFormat
        field6: *valueFormat
        field7: *valueFormat
        field8: *valueFormat
        field9: *valueFormat

Actors:
- Name: InsertActor
  Type: CrudActor
  Threads: {tc}
  Database: genny_qebench
  ClientName: EncryptedPool
  Phases:
  - *load_phase

{generateAutoRun()}

""")
