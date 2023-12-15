# Creating a Local Flink Environment

pre-requisites:

- Docker

# Step 1 - Setup the Docker-Compose File

- Open up an empty folder in your IDE
- Create a `docker-compose.yaml` file with the following

```yaml
###########################################
# Flink - Iceberg - Nessie Setup
###########################################

version: "3"

services:
# Nessie Catalog Server Using In-Memory Store
catalog:
  image: projectnessie/nessie
  container_name: catalog
  networks:
    iceberg-nessie-flink-net:
  ports:
    - 19120:19120
# Minio Storage Server
storage:
  image: minio/minio
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
  image: minio/mc
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
  image: alexmerced/flink-iceberg:latest
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
  image: alexmerced/flink-iceberg:latest
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
networks:
 iceberg-nessie-flink-net:

```

### Explanatio of this Dockerfile

**catalog:** This service uses the "projectnessie/nessie" Docker image and runs a Nessie Catalog Server using an in-memory store. It is assigned the container name "catalog" and exposes port 19120 for communication.

**storage:** This service uses the "minio/minio" Docker image and runs a Minio Storage Server. It is assigned the container name "storage" and is configured with environment variables for Minio, including a root user and password. It exposes ports 9001 and 9000 for communication and uses the command to start the Minio server with specific parameters.

**mc:** This service depends on the "storage" service and uses the "minio/mc" Docker image. It serves as a Minio Client container and is assigned the container name "mc." It sets environment variables for AWS access credentials and region. The entrypoint command configures the Minio client to connect to the Minio server and perform various Minio operations, such as creating buckets and setting policies.

**flink-jobmanager:** This service uses the "alexmerced/flink-iceberg:latest" Docker image and represents the Flink Job Manager. It exposes port 8081 for the Flink web interface. It sets environment variables related to Flink and AWS, specifying the job manager's RPC address and S3 endpoint for storage.

**flink-taskmanager:** This service also uses the "alexmerced/flink-iceberg:latest" Docker image and represents the Flink Task Manager. It depends on the "flink-jobmanager" service, indicating that it should only start after the job manager is ready. It sets environment variables for Flink properties, including the job manager's RPC address and the number of task slots. It also specifies AWS-related environment variables for authentication and S3 configuration.

# Step 2 - Run the Environment

You can start up all services in one terminal with:

```
docker-compose up
```

Or you can open up separate terminals for each service and run them in the order listed above.

```
docker-compose up storage

docker-compose up catalog

docker-compose up mc

docker-compose up flink-taskmanager

docker-compose up flink-jobmanager
```