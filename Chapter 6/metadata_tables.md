# Metadata Tables Reference

Here you'll find reference for Apache Iceberg Metadata tables for Chapter 6.

## Sample Data Sets

Below you'll find example values of each of the metadata tables for reference.
### History Table

| made_current_at             | snapshot_id          | parent_id             | is_current_ancestor |
|-----------------------------|----------------------|-----------------------|----------------------|
| 2023-02-08 03:29:51.215     | 5781947118336215154  | NULL                  | true                 |
| 2023-02-08 03:47:55.948     | 5179239526185256830  | 5781947118336215154  | true                 |
| 2023-02-09 16:24:30.13      | 296410040247533565   | 5179239526185256830  | false                |
| 2023-02-09 16:32:47.336     | 2999875608062437345  | 5179239526185256830  | true                 |


### Metadata Log Table

| timestamp                | file                 | latest_snapshot_id    | latest_schema_id    | latest_sequence_number |
|--------------------------|----------------------|-----------------------|---------------------|------------------------|
| 2023-07-28 10:43:52.93  | …/v1.metadata.json  | null                  | null                | null                   |
| 2023-07-28 10:43:57.487 | …/v2.metadata.json  | 760260833677645356    | 0                   | 1                      |

### Snapshots Table

| committed_at               | snapshot_id         | parent_id           | operation | manifest_list                | summary                                                                                                   |
|---------------------------|---------------------|---------------------|-----------|------------------------------|-----------------------------------------------------------------------------------------------------------|
| 2023-07-12 15:00:55.865   | 4434687458657877184 | null                |           |                              |                                                                                                           |
| 2023-07-12 15:05:29.566   | 8124673682209106082 | 4434687458657877184 | append    | s3://…085be5d55ef1.avro | {added-data-files -> 20, added-records -> 50, total-records -> 50, total-files-size -> 0, total-data-files -> 20, total-delete-files -> 0, total-position-deletes -> 0, total-equality-deletes -> 0} |


### Files Table

| content | file_path | file_format | spec_id | partition | record_count | file_size_in_bytes | columns_sizes | values_counts | null_value_counts | nan_value_counts | lower_bounds | upper_bounds | key_metadata | split_offsets | equality_ids | sort_order_id | readable_metrics |
|---------|-----------|-------------|---------|-----------|--------------|--------------------|---------------|--------------|------------------|-----------------|--------------|--------------|--------------|---------------|--------------|---------------|------------------|
| 0       | s3://…    | PARQUET     | 0       | {A}       | 6            | 609                | {1 -> 83}     | {1 -> 6}     | {1 -> 0}         | {1 -> 0}        | {}           | {}           | {1 -> Adriana} | null          | null         | null          | 0                |
| 0       | s3://…    | PARQUET     | 0       | {C}       | 5            | 596                | {1 -> 70}     | {1 -> 5}     | {1 -> 0}         | {1 -> 0}        | {}           | {}           | {1 -> Camila}  | null          | null         | null          | 0                |


### Manifests Table

| path     | length | partition_spec_id | added_snapshot_id | added_data_files_count | existing_data_files_count | deleted_data_files_count | partition_summaries |
|----------|--------|-------------------|-------------------|------------------------|---------------------------|-------------------------|---------------------|
| s3://…   | 6421   | 0                 | 1059035530770364194 | 16                    | 0                         | 0                       | [{false, false, A, V}] |
| s3://…   | 6501   | 0                 | 8616861888544170664 | 20                    | 0                         | 0                       | [{false, false, A, Z}] |

### Partitions Table

| partition | spec_id | record_count | file_count | position_delete_record_count | position_delete_file_count | equality_delete_record_count |
|-----------|---------|--------------|------------|-----------------------------|----------------------------|-------------------------------|
| {Z}       | 0       | 2            | 1          | 0                           | 0                          | 0                             |
| {W}       | 0       | 2            | 1          | 0                           | 0                          | 0                             |

### all_files table

| content | path     | file_format | spec_id | partition | record_count | file_size_in_bytes | column_sizes | values_counts | null_value_counts | nan_values_counts | lower_bounds | upper_bounds | key_metadata | split_offsets | equality_ids | sort_order_id | readable_metrics |
|---------|----------|-------------|---------|-----------|--------------|--------------------|--------------|---------------|-------------------|------------------|--------------|--------------|--------------|---------------|--------------|-----------------|
| 0       | s3://…   | PARQUET      | 0       | {A}       | 8            | 612                | {1 -> 94}    | {1 -> 8}      | {1 -> 0}         | {}               | {1 -> Abigail} | {1 -> Ava}   | null         | null          | null         | null            | 0               |
| 0       | s3://…   | PARQUET      | 0       | {B}       | 2            | 571                | {1 -> 48}    | {1 -> 2}      | {1 -> 0}         | {}               | {1 -> 0}      | {}           | null         | null          | null         | null            | 0               |
