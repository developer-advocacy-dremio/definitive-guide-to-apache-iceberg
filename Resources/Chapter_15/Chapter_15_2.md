# Resources for Chapter 15

### Data Producer

```py
import boto3
import requests
import json
import time


# Set AWS credentials within the script
aws_access_key_id = 'key'
aws_secret_access_key = 'secret'
region_name = 'region'  # Example: 'us-west-2'

# Set up Kinesis client
kinesis_client = boto3.client(
    'kinesis',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

STREAM_NAME = 'example_stream_book'  # Replace with your Kinesis stream name
OPENWEATHERMAP_API_KEY = 'key'  # Replace with your API key
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'

cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]

def get_weather_data(city):
    """Fetch weather data for a city."""
    url = WEATHER_API_URL.format(city, OPENWEATHERMAP_API_KEY)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for {city}. Reason: {response.text}")
        return None

def send_data_to_kinesis(data):
    """Send data to Kinesis stream."""
    payload = json.dumps(data)
    print(f"Sending payload: {payload}")
    
    # Put the data record into the Kinesis stream
    kinesis_client.put_record(
        StreamName=STREAM_NAME,
        Data=payload,
        PartitionKey=str(data['id'])  # Using city's weather 'id' as the partition key
    )

if __name__ == "__main__":
    for city in cities:
        data = get_weather_data(city)
        if data:
            send_data_to_kinesis(data)
        time.sleep(5)  # Introducing a short delay to not hit API rate limits and pace the inserts
```

Let’s break it down. e set up the Kinesis client and initialize it with boto3. The code then interacts with the OpenWeather API and fetches live weather information. The get_weather_data() method takes a city name as its parameter, constructs the relevant API URL, and then sends an HTTP request to fetch the weather details for that city. The function send_data_to_kinesis()pushes data to Kenisis. First, the weather data fetched is converted to a JSON-formatted string, suitable for transmission. Then the kinesis_client.put_record() method is invoked. This method pushes a single data record (in this case, the weather data) into the specified Kinesis stream (example_stream_book). A partition key is needed for proper sharding and streamlined data processing in Kinesis. We use the city's weather ‘id’ as a partition key to effectively distribute data across different shards.

### 13.2.2.3 Configuring the Job

**Handling Schema Enforcement Error in Apache Spark for Apache Iceberg tables**

```py
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

from pyspark.sql import DataFrame, Row
import datetime
from awsglue import DynamicFrame
from awsglue import DynamicFrame


def sparkSqlQuery(glueContext, query, mapping, transformation_ctx) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)


args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node Amazon Kinesis
dataframe_AmazonKinesis_node1693319486385 = glueContext.create_data_frame.from_options(
    connection_type="kinesis",
    connection_options={
        "typeOfData": "kinesis",
        "streamARN": "arn:aws:kinesis:us-east-1:328716720259:stream/example_stream_book",
        "classification": "json",
        "startingPosition": "latest",
        "inferSchema": "true",
    },
    transformation_ctx="dataframe_AmazonKinesis_node1693319486385",
)


def processBatch(data_frame, batchId):
    if data_frame.count() > 0:
        AmazonKinesis_node1693319486385 = DynamicFrame.fromDF(
            data_frame, glueContext, "from_data_frame"
        )
        # Script generated for node Create Table
        SqlQuery0 = """
        CREATE TABLE IF NOT EXISTS glue.dip.my_streaming_data AS 
        (SELECT * FROM myDataSource LIMIT 0);
        """
        CreateTable_node1693319510128 = sparkSqlQuery(
            glueContext,
            query=SqlQuery0,
            mapping={"myDataSource": AmazonKinesis_node1693319486385},
            transformation_ctx="CreateTable_node1693319510128",
        )

        # Script generated for node Insert Into
        SqlQuery1 = """
        INSERT INTO glue.dip.my_streaming_data SELECT * FROM myDataSource;
        """
        InsertInto_node1693319537299 = sparkSqlQuery(
            glueContext,
            query=SqlQuery1,
            mapping={"myDataSource": AmazonKinesis_node1693319486385},
            transformation_ctx="InsertInto_node1693319537299",
        )


glueContext.forEachBatch(
    frame=dataframe_AmazonKinesis_node1693319486385,
    batch_function=processBatch,
    options={
        "windowSize": "100 seconds",
        "checkpointLocation": args["TempDir"] + "/" + args["JOB_NAME"] + "/checkpoint/",
    },
)
job.commit()
```

### 13.4.1 Use Case 1: Reliable ML Pipelines

```py
from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException

def ingest_new_data(new_data_path, iceberg_table_name):
    """
    Ingest new data into an existing Iceberg table
    
    Args:
    - new_data_path: The path to the new dataset to ingest.
    - iceberg_table_name: The name of the existing Iceberg table to ingest data into.
    """
    try:
        # Load the new data
        new_df = spark.read.csv(new_data_path, header=True, inferSchema=True)
        
        # Try to append the new data to the existing table
        new_df.write.format("iceberg").mode("append").saveAsTable(iceberg_table_name)
        print(f"Data from {new_data_path} ingested successfully into {iceberg_table_name}!")
        
    except AnalysisException as ae:
        # Catch any errors during the write operation, including schema mismatch errors
        print(f"Error ingesting data into {iceberg_table_name}: {str(ae)}")
        

# Ingest new data
new_data_path = "churn_etl_new.csv" 
iceberg_table_name = "glue.test.churn"
ingest_new_data(new_data_path, iceberg_table_name)

------------------------------------------------------------
# Error ingesting data into glue.test.churn: Cannot write incompatible data to table 'Iceberg glue.test.churn':
- Cannot safely cast 'Account_length': string to int
```

**Schema Validation Before Ingestion**

```py
from pyspark.sql.types import StructType, StringType, IntegerType, FloatType, BooleanType, StructField
from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException


def validate_and_ingest(new_data_path, iceberg_table_name):
    """
    Validate the schema of the new dataset against the schema of an existing Iceberg table 
    and ingest the new data if the schemas match.
    
    Args:
    - new_data_path: The path to the new dataset to ingest.
    - iceberg_table_name: The name of the existing Iceberg table to validate against.
    """
    try:
        # Load the schema of the existing Iceberg table
        existing_df = spark.table(iceberg_table_name)
        existing_schema = existing_df.schema
        
        # Load the new data
        new_df = spark.read.csv(new_data_path, header=True, inferSchema=True)
        
        # Check the schema of the new data against the schema of the existing Iceberg table
        if str(new_df.schema) != str(existing_schema):
            raise ValueError("Schema mismatch detected in the new data!")
        
        # If no errors, append the new data to the existing table
        new_df.writeTo(iceberg_table_name).append()
        print(f"Data from {new_data_path} ingested successfully into {iceberg_table_name}!")
        
    except AnalysisException:
        print(f"Error reading the data from {new_data_path} or the Iceberg table {iceberg_table_name}.")
    except ValueError as ve:
        print(ve)

# Validate and ingest new data
new_data_path = "churn_etl.csv"  
iceberg_table_name = "glue.test.churn"
validate_and_ingest(new_data_path, iceberg_table_name)
```

### 13.4.2.1 Use Case 2: ML Reproducability Solutions

**Modeling Data on earlier snapshot via time travel**

```py
from pyspark.sql import SparkSession
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# Retrieve a specific snapshot of the Iceberg table from a week ago
snapshot_id_of_interest = 5889239598709613914  

df = spark.read \
    .option("snapshot-id", snapshot_id_of_interest) \
    .format("iceberg") \
    .load("glue.test.churn")

# Convert to Pandas for ML operations
pdf = df.toPandas()

# Split data 
pdf.drop(['State', 'Area_code'], axis=1, inplace=True)

# dummy categorical data
pdf['International_plan']=pdf['International_plan'].replace(['No','Yes'],[0,1])
pdf['Voicemail_plan']=pdf['Voicemail_plan'].replace(['No','Yes'],[0,1])
pdf['Churn']=pdf['Churn'].replace(['FALSE', 'TRUE'],[0,1])

#prepare data 
target = pdf.iloc[: , -1].values
features = pdf.iloc[: , : -1].values

# divide train & test data
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.20,random_state=101)

# Train a model
clf = RandomForestClassifier()
clf.fit(X_train, y_train)

# Make predictions and check accuracy
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Model accuracy on data from snapshot {snapshot_id_of_interest}: {accuracy * 100:.2f}%")


# Model accuracy on data from snapshot 5889239598709613914: 93.58%
```

**Training a Model against consistent data using Tags**

```py
from pyspark.sql import SparkSession
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


df = spark.read \
    .option("tags", 'June_23') \
    .format("iceberg") \
    .load("glue.test.churn")

pdf = df.toPandas()

# Split data 
pdf.drop(['State', 'Area_code'], axis=1, inplace=True)

# dummy categorical data
pdf['International_plan']=pdf['International_plan'].replace(['No','Yes'],[0,1])
pdf['Voicemail_plan']=pdf['Voicemail_plan'].replace(['No','Yes'],[0,1])
pdf['Churn']=pdf['Churn'].replace(['FALSE', 'TRUE'],[0,1])

#prepare data 
target = pdf.iloc[: , -1].values
features = pdf.iloc[: , : -1].values

# divide train & test data
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.20,random_state=101)

# Train a model
clf = RandomForestClassifier()
clf.fit(X_train, y_train)

# Make predictions and check accuracy
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Model accuracy on data from snapshot {snapshot_id_of_interest}: {accuracy * 100:.2f}%")
```

### 13.4.3 Support ML Experiementation

```py
from pyspark.sql import SparkSession
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


df_prem = spark.read \
    .option("branch", 'Churn_PremiumExp') \
    .format("iceberg") \
    .load("glue.test.churn_new")

# Convert to Pandas for ML operations
pdf = df_prem.toPandas()

# Split data 
pdf.drop(['State', 'Area_code'], axis=1, inplace=True)

# dummy categorical data
pdf['International_plan']=pdf['International_plan'].replace(['No','Yes'],[0,1])
pdf['Voicemail_plan']=pdf['Voicemail_plan'].replace(['No','Yes'],[0,1])
pdf['Churn']=pdf['Churn'].replace(['FALSE', 'TRUE'],[0,1])

#prepare data 
target = pdf.iloc[: , -1].values
features = pdf.iloc[: , : -1].values

# divide train & test data
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.20,random_state=101)

# Train a model
clf = RandomForestClassifier()
clf.fit(X_train, y_train)

# Make predictions and check accuracy
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Model accuracy on data from snapshot {snapshot_id_of_interest}: {accuracy * 100:.2f}%")

Post-experimentation, if the team finds the new dataset invaluable, they might consider making the data available to the main table. Alternatively, if the experiment doesn't provide substantial gains, they can safely discard the branch, ensuring the main table remains streamlined:

spark.sql("ALTER TABLE glue.test.churn DROP BRANCH Churn_PremiumExp")
```

### 13.6.1 Creating Fact & Dimension Tables to prepare for SCD2

**Creating the Customers Table**

```py
dim_customer_schema = StructType([
        StructField('customer_id', StringType(), False),
        StructField('first_name', StringType(), True),
        StructField('last_name', StringType(), True),
        StructField('city', StringType(), True),
        StructField('country', StringType(), True),
        StructField('eff_start_date', DateType(), True),
        StructField('eff_end_date', DateType(), True),
        StructField('timestamp', TimestampType(), True),
        StructField('is_current', BooleanType(), True),
    ])

random_udf = udf(lambda: str(int(time.time() * 1000000)), StringType()) 

from datetime import datetime

customer_dim_df = spark.createDataFrame([('1', 'Morgan', 'Brown', 'Toronto', 'Canada', datetime.strptime('2020-09-27', '%Y-%m-%d'), datetime.strptime('2999-12-31', '%Y-%m-%d'), datetime.strptime('2020-12-08 09:15:32', '%Y-%m-%d %H:%M:%S'), True),
                       ('2', 'Angie', 'Keller', 'Chicago', 'US', datetime.strptime('2020-10-14', '%Y-%m-%d'), datetime.strptime('2999-12-31', '%Y-%m-%d'), datetime.strptime('2020-12-08 09:15:32', '%Y-%m-%d %H:%M:%S'), True)], dim_customer_schema)

customer_ice_df = customer_dim_df.withColumn("customer_dim_key", random_udf())

customer_ice_df.cache()
customer_ice_df.writeTo("glue.dip.customers").partitionedBy(col("country")).create()

```

**Creating the Sales Table**

```py
from pyspark.sql.functions import to_timestamp

fact_sales_schema = StructType([
        StructField('item_id', StringType(), True),
        StructField('quantity', IntegerType(), True),
        StructField('price', DoubleType(), True),
        StructField('timestamp', TimestampType(), True),
        StructField('customer_id', StringType(), True)
    ])

sales_fact_df = spark.createDataFrame([('111', 40, 90.5, datetime.strptime('2020-11-17 09:15:32', '%Y-%m-%d %H:%M:%S'), '1'),
                                       ('112', 250, 80.65, datetime.strptime('2020-10-28 09:15:32', '%Y-%m-%d %H:%M:%S'), '1'),
                                      ('113', 10, 600.5, datetime.strptime('2020-12-08 09:15:32', '%Y-%m-%d %H:%M:%S'), '2')], fact_sales_schema)

sales_fact_df.show()

+-------+--------+-----+-------------------+-----------+
|item_id|quantity|price|          timestamp|customer_id|
+-------+--------+-----+-------------------+-----------+
|    111|      40| 90.5|2020-11-17 09:15:32|          1|
|    112|     250|80.65|2020-10-28 09:15:32|          1|
|    113|      10|600.5|2020-12-08 09:15:32|          2|
+-------+--------+-----+-------------------+-----------+
```