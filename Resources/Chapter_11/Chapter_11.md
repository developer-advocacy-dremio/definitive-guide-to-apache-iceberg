# Chapter 11 Resources

### Example of Streaming Iceberg with Flink

This job does the following:
- Creates a Hive Catalog for the Table Environment
- Query the aggregated state for the current days sales data for all dates in the current month
- INSERT OVERWRITE into the aggregate table replacing that current months partition with the updated data
- Put the thread sleep for an hour in which the task will run again


```java
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.EnvironmentSettings;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

public class SalesDataSummaryJob {

    public static void main(String[] args) throws Exception {
        // Initialize Flink environment
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        EnvironmentSettings settings = EnvironmentSettings.newInstance().useBlinkPlanner().inStreamingMode().build();
        StreamTableEnvironment tEnv = StreamTableEnvironment.create(env, settings);

        // Create Hive Catalog
        String catalogName = "myhive";
        String catalogType = "iceberg";
        String hiveCatalogUri = "thrift://localhost:9083";
        String warehousePath = "s3://someBucket/warehouse/path";
        String hiveClientConfig = "5";

        String createCatalogStatement = "CREATE CATALOG " + catalogName + " WITH (\n" +
                "'type'='" + catalogType + "',\n" +
                "'catalog-type'='hive',\n" +
                "'uri'='" + hiveCatalogUri + "',\n" +
                "'warehouse'='" + warehousePath + "',\n" +
                "'clients'='" + hiveClientConfig + "',\n" +
                "'property-version'='1'\n" +
                ")";

        // Register Hive Catalog
        tEnv.executeSql(createCatalogStatement);
        tEnv.useCatalog(catalogName);

        // Define the source and destination table names
        String sourceTableName = "retail_sales_data";
        String destinationTableName = "sales_data_summary";

        // Calculate the current month's partition value (e.g., '2023-08' for August 2023)
        String currentMonthPartition = getCurrentMonthPartition();

        // SQL query to process data for the current month
        String sqlQuery = "INSERT OVERWRITE " + destinationTableName + " PARTITION (month = '" + currentMonthPartition + "') " +
                "SELECT date, SUM(sales_amount) as total_sales " +
                "FROM " + sourceTableName + " " +
                "WHERE month = '" + currentMonthPartition + "' " +
                "GROUP BY date";

        // Execute the SQL query
        tEnv.executeSql(sqlQuery);

        // Sleep for one hour before executing the job again
        Thread.sleep(3600000);
    }

    private static String getCurrentMonthPartition() {
        LocalDate currentDate = LocalDate.now();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM");
        return currentDate.format(formatter);
    }
}
```

### Summary

| Aspect/Feature             | Apache Spark Streaming  | Apache Flink                          | AWS Kinesis                 | Kafka Connect                |
|----------------------------|-------------------------|---------------------------------------|-----------------------------|-----------------------------|
| Open Source                | Yes                     | Yes                                   | No                          | Yes                         |
| Processing Model           | Micro-batching          | Stream-based                          | Stream-based                | Stream-based                |
| Latency                    | Higher (seconds)        | Low (ms)                              | Low (ms)                    | N/A (Data integration tool) |
| State Management           | Yes                     | Yes                                   | Yes                         | N/A                         |
| Fault Tolerance            | Yes                     | Yes                                   | Yes                         | Yes                         |
| Scalability                | Yes                     | Yes                                   | Yes                         | Yes                         |
| Integration with Kafka     | Yes                     | Yes                                   | Via Connectors              | Native                      |
| Windowing Support          | Yes                     | Yes                                   | Yes                         | N/A                         |
| API Languages              | Scala, Java, Python     | Java, Scala                           | Java, .NET, etc.            | Java, Scala                 |
| Use Case Focus             | General-purpose stream processing | Real-time analytics & General-purpose stream processing | Real-time analytics & stream processing | Data Integration |
