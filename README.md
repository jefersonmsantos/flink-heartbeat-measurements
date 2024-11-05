datagen -> cloud run
kafka cluster - > gcp
deploy flink -> docker on VM?


docker buildx build --platform linux/amd64 -t datagen:1.0 .
docker tag datagen:latest us-central1-docker.pkg.dev/edc-igti-325912/docker-registry/datagen:latest
docker push us-central1-docker.pkg.dev/edc-igti-325912/docker-registry/datagen:latest

docker buildx build --platform linux/arm64/v8 --no-cache --tag pyflink:latest .

protoc --python_out=. sample_data.proto 

./flink-1.17.1/bin/flink run --python ./heartbeat_avg.py --pyFiles ./sample_data_pb2.py


docker tag pyflink:amd us-central1-docker.pkg.dev/edc-igti-325912/docker-registry/pyflink:latest
docker push us-central1-docker.pkg.dev/edc-igti-325912/docker-registry/pyflink:latest

install requirements. have same python version as host
python3.10 needs pip install --upgrade protobuf
auth bigquery


- Create VM
- INstall docker - docker-compose
    [install docker](https://docs.docker.com/engine/install/ubuntu/)

- Install JAVA11
    sudo apt-get update
    sudo apt-get install -y openjdk-11-jdk python3 python3-pip python3-dev && sudo rm -rf /var/lib/apt/lists/*
    sudo ln -s /usr/bin/python3 /usr/bin/python
    pip install apache-flink==1.20.0 cloudpickle==2.2.1 apache-beam==2.48.0 google-cloud==0.34.0 google_cloud_bigquery_storage==2.26.0 protobuf
    pip install --upgrade protobuf
- Install Python
- Download flink
    curl https://archive.apache.org/dist/flink/flink-1.17.1/flink-1.17.1-bin-scala_2.12.tgz --output flink-1.17.1.tgz
    tar -xzf flink-*.tgz


- Upload files
    gcloud storage

- Spin up conteiners
- Submit job


base64 < my_service_account.json > password.txt