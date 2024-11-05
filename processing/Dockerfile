FROM flink:1.17.1

# install python3 and pip3
RUN apt-get update -y && \
apt install -y software-properties-common && \
apt-get install -y openjdk-11-jdk python3 python3-pip && rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/python3 /usr/bin/python

# install PyFlink
#ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64
COPY requirements.txt /opt/app/requirements.txt
RUN python3 -m pip install -r /opt/app/requirements.txt
RUN python3 -m pip install --upgrade protobuf