# Creating a Data Lakehouse Evironment for Experiementing with Apache Iceberg Locally

**pre-requisites:**
- Docker Installed

## Setup

In your favorite IDE open up a an empty folder/workspace and create a `docker-compose.yaml` file with the following:

```yaml
###########################################
# Flink - Iceberg - Nessie Setup
###########################################

version: "3"

services:
  # Spark Notebook Server
  spark-iceberg:
    image: alexmerced/spark33-notebook
    container_name: spark-iceberg
    networks:
      iceberg-nessie-flink-net:
    depends_on:
      - catalog
      - storage
    volumes:
      - ./warehouse:/home/docker/warehouse
      - ./notebooks:/home/docker/notebooks
      - ./datasets:/home/docker/datasets
    environment:
      - AWS_ACCESS_KEY_ID=admin
      - AWS_SECRET_ACCESS_KEY=password
      - AWS_REGION=us-east-1
      - AWS_DEFAULT_REGION=us-east-1
    ports:
      - 8888:8888
      - 8080:8080
      - 10000:10000
      - 10001:10001
  # Nessie Catalog Server Using In-Memory Store
  catalog:
    image: projectnessie/nessie:0.67.0
    container_name: catalog
    networks:
      iceberg-nessie-flink-net:
    ports:
      - 19120:19120
  # Minio Storage Server
  storage:
    image: minio/minio:RELEASE.2023-07-21T21-12-44Z
    container_name: storage
    environment:
      - MINIO_ROOT_USER=admin
      - MINIO_ROOT_PASSWORD=password
      - MINIO_DOMAIN=storage
      - MINIO_REGION_NAME=us-east-1
      - MINIO_REGION=us-east-1
    networks:
      iceberg-nessie-flink-net:
    ports:
      - 9001:9001
      - 9000:9000
    command: ["server", "/data", "--console-address", ":9001"]
  # Minio Client Container
  mc:
    depends_on:
      - storage
    image: minio/mc:RELEASE.2023-07-21T20-44-27Z
    container_name: mc
    networks:
      iceberg-nessie-flink-net:
        aliases:
          - minio.storage
    environment:
      - AWS_ACCESS_KEY_ID=admin
      - AWS_SECRET_ACCESS_KEY=password
      - AWS_REGION=us-east-1
      - AWS_DEFAULT_REGION=us-east-1
    entrypoint: >
      /bin/sh -c "
      until (/usr/bin/mc config host add minio http://storage:9000 admin password) do echo '...waiting...' && sleep 1; done;
      /usr/bin/mc rm -r --force minio/warehouse;
      /usr/bin/mc mb minio/warehouse;
      /usr/bin/mc mb minio/iceberg;
      /usr/bin/mc policy set public minio/warehouse;
      /usr/bin/mc policy set public minio/iceberg;
      tail -f /dev/null
      "
  # Flink Job Manager
  flink-jobmanager:
    image: alexmerced/iceberg-flink-1.3.1
    ports:
      - "8081:8081"
    command: jobmanager
    networks:
      iceberg-nessie-flink-net:
    environment:
      - |
        FLINK_PROPERTIES=
        jobmanager.rpc.address: flink-jobmanager
      - AWS_ACCESS_KEY_ID=admin
      - AWS_SECRET_ACCESS_KEY=password
      - AWS_REGION=us-east-1
      - AWS_DEFAULT_REGION=us-east-1
      - S3_ENDPOINT=http://minio.storage:9000
      - S3_PATH_STYLE_ACCESS=true
  # Flink Task Manager
  flink-taskmanager:
    image: alexmerced/iceberg-flink-1.3.1
    depends_on:
      - flink-jobmanager
    command: taskmanager
    networks:
      iceberg-nessie-flink-net:
    scale: 1
    environment:
      - |
        FLINK_PROPERTIES=
        jobmanager.rpc.address: flink-jobmanager
        taskmanager.numberOfTaskSlots: 2
      - AWS_ACCESS_KEY_ID=admin
      - AWS_SECRET_ACCESS_KEY=password
      - AWS_REGION=us-east-1
      - AWS_DEFAULT_REGION=us-east-1
      - S3_ENDPOINT=http://minio.storage:9000
      - S3_PATH_STYLE_ACCESS=true
  # Dremio
  dremio:
    platform: linux/x86_64
    image: dremio/dremio-oss:latest
    ports:
      - 9047:9047
      - 31010:31010
      - 32010:32010
    container_name: dremio
    networks:
      iceberg-nessie-flink-net:
networks:
  iceberg-nessie-flink-net:
```

You can find an example at the follow repository:

[Example Data Engineer Dev Environment Repo](https://github.com/developer-advocacy-dremio/apache-iceberg-tutorial-environment)

## Start Up

Now follow these direction to start up each service (each command should be run in seperate terminal windows):


- `docker-compose up catalog` this will create a Nessie catalog server

- `docker-compose up storage` this will create a minio server accessible on localhost:9000

- `docker-compose up mc` this will start the minio client which will create our initial buckets

- `docker-compose up spark-iceberg` this will open up a Spark container with a Jupyter Notebook server for writing pyspace scripts running on localhost:8080. Make sure to check the terminal for the token to access the notebook server.

- `docker-compose up flink-jobmanager` this will open up a flink instance acting as a job manager accessible on localhost:8081.

- `docker-compose up flink-taskmanager` this will open up a flink instance acting as a task manager

- `docker-compose up dremio` will create an instance of dremio accessible at localhost:9047

## Tear Down

- To turn off all the containers run `docker-compose down`

- To turn off one container at a time run `docker-compose down container_name` using the same names from the startup section.

## Configuring PySpark

Using the above setup you configure pyspark with the following settings:

```py
import pyspark
from pyspark.sql import SparkSession
import os


## DEFINE SENSITIVE VARIABLES
NESSIE_URI = "http://nessie:19120/api/v1" ## Nessie Server URI
WAREHOUSE = "s3a://warehouse/" ## BUCKET TO WRITE DATA TOO
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY") ## AWS CREDENTIALS
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY") ## AWS CREDENTIALS
AWS_S3_ENDPOINT= os.environ.get("AWS_S3_ENDPOINT") ## MINIO ENDPOINT


print(AWS_S3_ENDPOINT)
print(NESSIE_URI)
print(WAREHOUSE)


conf = (
    pyspark.SparkConf()
        .setAppName('app_name')
        .set('spark.jars.packages', 'org.apache.iceberg:iceberg-spark-runtime-3.3_2.12:1.3.1,org.projectnessie.nessie-integrations:nessie-spark-extensions-3.3_2.12:0.67.0,software.amazon.awssdk:bundle:2.17.178,software.amazon.awssdk:url-connection-client:2.17.178')
        .set('spark.sql.extensions', 'org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,org.projectnessie.spark.extensions.NessieSparkSessionExtensions')
        .set('spark.sql.catalog.nessie', 'org.apache.iceberg.spark.SparkCatalog')
        .set('spark.sql.catalog.nessie.uri', NESSIE_URI)
        .set('spark.sql.catalog.nessie.ref', 'main')
        .set('spark.sql.catalog.nessie.authentication.type', 'NONE')
        .set('spark.sql.catalog.nessie.catalog-impl', 'org.apache.iceberg.nessie.NessieCatalog')
        .set('spark.sql.catalog.nessie.s3.endpoint', AWS_S3_ENDPOINT)
        .set('spark.sql.catalog.nessie.warehouse', WAREHOUSE)
        .set('spark.sql.catalog.nessie.io-impl', 'org.apache.iceberg.aws.s3.S3FileIO')
        .set('spark.hadoop.fs.s3a.access.key', AWS_ACCESS_KEY)
        .set('spark.hadoop.fs.s3a.secret.key', AWS_SECRET_KEY)
)


## Start Spark Session
spark = SparkSession.builder.config(conf=conf).getOrCreate()
print("Spark Running")


## Create a Table (make sure to use table actually in catalog)
spark.sql("SELECT * FROM nessie.db.table").show()
```