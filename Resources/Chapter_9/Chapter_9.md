# Chapter 9 Resources

```java
package com.my_flink_job;

import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableResult;
import org.apache.flink.table.api.EnvironmentSettings;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import static org.apache.flink.table.api.Expressions.$;
import com.my_flink_job.EmployeeData;

public class App
{
    public static void main(String[] args) throws Exception {

        // set up the execution environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // set up the table environment
        final StreamTableEnvironment tableEnv = StreamTableEnvironment.create(
                env,
                EnvironmentSettings.newInstance().inStreamingMode().build());

        // create the Nessie catalog
        tableEnv.executeSql(
                "CREATE CATALOG iceberg WITH ("
                        + "'type'='iceberg',"
                        + "'catalog-impl'='org.apache.iceberg.nessie.NessieCatalog',"
                        + "'io-impl'='org.apache.iceberg.aws.s3.S3FileIO',"
                        + "'uri'='http://catalog:19120/api/v1',"
                        + "'authentication.type'='none',"
                        + "'ref'='main',"
                        + "'client.assume-role.region'='us-east-1',"
                        + "'warehouse' = 's3://warehouse',"
                        + "'s3.endpoint'='http://{id-address}:9000'"
                        + ")");

        // List all catalogs
        TableResult result = tableEnv.executeSql("SHOW CATALOGS");
        result.print();

        // Set the current catalog to the new catalog
        tableEnv.useCatalog("iceberg");

        // Create a database in the current catalog
        tableEnv.executeSql("CREATE DATABASE IF NOT EXISTS db");

        // create the table
        tableEnv.executeSql(
                "CREATE TABLE IF NOT EXISTS db.employees ("
                        + "id BIGINT COMMENT 'unique id',"
                        + "department STRING,"
                        + "salary BIGINT"
                        + ")");


        // create a DataStream of Tuple3 (equivalent to Row of 3 fields)
        DataStream<Tuple3<Long, String, Long>> dataStream = env.fromElements(
                Tuple3.of(1L, "HR", 50000L),
                Tuple3.of(2L, "Engineering", 70000L),
                Tuple3.of(3L, "Marketing", 60000L));


        // apply a map transformation to convert the Tuple3 to an EmployeeData object
        DataStream<EmployeeData> mappedStream = dataStream.map(new MapFunction<Tuple3<Long, String, Long>, EmployeeData>() {
            @Override
            public EmployeeData map(Tuple3<Long, String, Long> value) throws Exception {
                // your mapping logic 
                return new EmployeeData(value.f0, value.f1, value.f2);
            }
        });

        // convert the DataStream to a Table
        Table table = tableEnv.fromDataStream(mappedStream, $("id"), $("department"), $("salary"));

        // register the Table as a temporary view
        tableEnv.createTemporaryView("my_datastream", table);

        // write the DataStream to the table
        tableEnv.executeSql(
                "INSERT INTO db.employees SELECT * FROM my_datastream");
    }
}
```