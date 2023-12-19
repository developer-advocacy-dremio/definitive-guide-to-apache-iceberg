# Chapter 3 Resources

### Merge Query

Example of a Manifest File

```json
{
"data_file" : {
	"file_path" :
"s3://datalake/db1/orders/data/order_ts_hour=2023-01-27-10/0_0_0.parquet",
"file_format" : "PARQUET",
     	"block_size_in_bytes" : 67108864,
     	"null_value_counts" : [],
     	"lower_bounds" : {
		"array": [{
"key": 1,
		"value": 125
}],
}
     	"upper_bounds" : {
		"array": [{
"key": 1,
		"value": 125
}],
}
   },
	"data_file" : {
	"file_path" :
"s3://datalake/db1/orders/data/order_ts_hour=2023-03-07-08/0_0_1.parquet",
"file_format" : "PARQUET",
     	"block_size_in_bytes" : 67108864,
     	"null_value_counts" : [],
     	"lower_bounds" : {
		"array": [{
"key": 1,
		"value": 123
}],
}
     	"upper_bounds" : {
		"array": [{
"key": 2,
		"value": 200
}],
}
}

}
```

Example of Manifest List after update

```json
{
 "manifest_path":
"s3://datalake/db1/orders/metadata/faf71ac0-3aee-4910-9080-c2e688148066.avro",
 "manifest_length": 6196,
 "added_snapshot_id": 5139476312242609518,
 "added_data_files_count": 2,
 "added_rows_count": 2,
 "partitions": {
        "array": [ {
            "contains_null": false,
            "lower_bound": {
                "bytes": "¹Ô\\u0006\\u0000"
            },
            "upper_bound": {
                "bytes": "¹Ô\\u0006\\u0000"
            }
        } ]
    }
}
{
 "manifest_path":
"s3://datalake/db1/orders/metadata/e22ff753-2738-4d7d-a810-d65dcc1abe63-m0.avro",
 "manifest_length": 6162,
 "added_snapshot_id": 5139476312242609518,
 "added_data_files_count": 0,
 "added_rows_count": 0,
  . . . . . .
}
```

Example of Metadata.json after update

```json
"current-snapshot-id" : 5139476312242609518,
  	"refs" : {
    	"main" :  {
     	"snapshot-id" : 5139476312242609518,
      	"type" : "branch"
}
},
"snapshots" : [ {
    "snapshot-id" : 5139476312242609518,
    "summary" : {
      "operation" : "overwrite",
      "added-data-files" : "2",
 "deleted-data-files" : "1",
      "added-records" : "2",
},
   "manifest-list" : s3://datalake/db1/orders/metadata/snap-5139476312242609518-1-e22ff753-2738-4d7d-a810-d65dcc1abe63.avro",
  } ],

```

### SELECT Query

The Schema Data from the metadata.json

```json
"schema" : {
    "type" : "struct",
    "schema-id" : 0,
    "fields" : [ {
      "id" : 1,
      "name" : "order_id",
      "required" : false,
      "type" : "long"
    }, {
      "id" : 2,
      "name" : "customer_id",
      "required" : false,
      "type" : "long"
    }, {
      "id" : 3,
      "name" : "order_amount",
      "required" : false,
      "type" : "decimal(10, 2)"
    }, {
      "id" : 4,
      "name" : "order_ts",
      "required" : false,
      "type" : "timestamptz"
    } ]
  },
```

The Partition Schemes in the metadata.json

```json
"partition-spec" : [ {
    "name" : "order_ts_hour",
    "transform" : "hour",
    "source-id" : 4,
    "field-id" : 1000
  } ]
```

Finding the Current Snapshot Data in the metadata.json:

```json
"current-snapshot-id" : 5139476312242609518,
  "refs" : {
    "main" : {
      "snapshot-id" : 5139476312242609518,
      "type" : "branch"
    }
  },
"snapshots" : [{
    "snapshot-id" : 7327164675870333694,
    "manifest-list" : "s3://datalake/db1/orders/metadata/snap-7327164675870333694-1-f5e79df9-7027-4d0c-a39b-7a3091741d6f.avro",
    "schema-id" : 0
  },
{
    "snapshot-id" : 5139476312242609518,
    "parent-snapshot-id" : 8333017788700497002,
    "manifest-list" : "s3://datalake/db1/orders/metadata/snap-5139476312242609518-1-e22ff753-2738-4d7d-a810-d65dcc1abe63.avro",
    "schema-id" : 0
  },
{
    "snapshot-id" : 8333017788700497002,
    "parent-snapshot-id" : 7327164675870333694
    "manifest-list" : "s3://datalake/db1/orders/metadata/snap-8333017788700497002-1-4010cc03-5585-458c-9fdc-188de318c3e6.avro",
    "schema-id" : 0
  }
]
```

Getting Information from the manifest list

```json
{
"manifest_path" : "s3://datalake/db1/orders/metadata/faf71ac0-3aee-4910-9080-c2e688148066.avro",
    "partition_spec_id" : 0,
    "added_snapshot_id" : 5139476312242609518,
    "added_data_files_count" : 2,
    "partitions" : [
        {   
"contains_null" : false,
"contains_nan" : false,
"lower_bound" : "ShkHAA==",
"upper_bound" : "8BwHAA=="
        }
    ],}
```

Partition Data in a Manifest File

```json
"partition" : {
"order_ts_hour" : 2023-01-27-10
        },
"partition" : {
"order_ts_hour" : 2023-03-07-08
        },
```

Data File stats that can be used for fine-grained file pruning during query planning. These stats are found in manifests for an individual data file.

```json
"data_file" : {
"file_path" :
"s3://datalake/db1/orders/data/order_ts_hour=2023-01-27-10/0_0_0.parquet",
"partition" : {
"order_ts_hour" : 2023-01-27-10
        },
	"lower_bounds" : [{
"key" : 1,
"value" : "fQAAAAAAAAA="
            },
            {     
"key" : 2,
"value" : "QQEAAAAAAAA="
            }],
	"upper_bounds" : [{
"key" : 1,
"value" : "fQAAAAAAAAA="
            },
            {     
"key" : 2,
"value" : "QQEAAAAAAAA="
            }],
},

"data_file" : {
"file_path" :
"s3://datalake/db1/orders/data/order_ts_hour=2023-03-07-08/0_0_1.parquet",
"partition" : {
"order_ts_hour" : 2023-03-07-08
        },
},
```

### Time-Travel Query

Based on this information, the corresponding snapshot is as presented below. Note that the timestamp value is in millisecond UNIX epoch format in the metadata file (1678221908914), which, when converted to date-time format, is March 7, 2023 8:45:08.914. This value matches our time travel query. 

```json
	{
    "snapshot-id" : 7327164675870333694,
    "timestamp-ms" : 1678138115360,
    "summary" : {
      "operation" : "append",
      "total-records" : "0",
      "total-files-size" : "0",
     },
    "manifest-list" : "s3://datalake/db1/orders/metadata/snap-7327164675870333694-1-f5e79df9-7027-4d0c-a39b-7a3091741d6f.avro",
    "schema-id" : 0
  }, 
{
    "snapshot-id" : 8333017788700497002,
    "parent-snapshot-id" : 7327164675870333694,
    "timestamp-ms" : 1678221908914,
    "summary" : {
      "operation" : "append",
      "added-data-files" : "1",
      "added-records" : "1",
      "total-records" : "1",
    },
    "manifest-list" : "s3://datalake/db1/orders/metadata/snap-8333017788700497002-1-4010cc03-5585-458c-9fdc-188de318c3e6.avro",}

```

Based on the manifest list path, the engine opens and reads the snap-8333017788700497002-1-4010cc03-5585-458c-9fdc-188de318c3e6.avro file.

Here is the content of this manifest list.


```json
{    "manifest_path" : "s3://datalake/db1/orders/metadata/62acb3d7-e992-4cbc-8e41-58809fcacb3e.avro",
    "manifest_length" : 6152,
    "partition_spec_id" : 0,
    "added_snapshot_id" : 8333017788700497000,
    "added_data_files_count" : 1,
    "existing_data_files_count" : 0,
    "deleted_data_files_count" : 0,
    "partitions" : [
        {   
"contains_null" : false,
"contains_nan" : false,
"lower_bound" : "8BwHAA==",
"upper_bound" : "8BwHAA=="
        }
    ],
    "added_rows_count" : 1,
    "deleted_rows_count" : 0
}
```

A manifest with a single data file after a time travel query

```json
	"data_file" : {
        "file_path" : "s3://datalake/db1/orders/data/order_ts_hour=2023-03-07-08/0_0_0.parquet",
        "file_format" : "PARQUET",
        "partition" : {
            "order_ts_hour" : 2023-03-07-08
        },
   "lower_bounds" : [
            {
"key" : 1,
"value" : "ewAAAAAAAAA="
            } ],
	   "upper_bounds" : [
            {
"key" : 1,
"value" : "ewAAAAAAAAA="
            } ],
}
```