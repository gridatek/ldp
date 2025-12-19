FROM python:3.14-slim

USER root

# Install system dependencies including Java
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-17-jdk-headless \
    wget \
    curl \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# Download and install Apache Spark 4.0.1
ENV SPARK_VERSION=4.0.1
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip:$PYTHONPATH

RUN wget -q https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME} && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# Install Python packages from requirements.txt
COPY docker/spark/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Install additional Python packages for Spark
RUN pip install --no-cache-dir \
    boto3 \
    s3fs

# Copy custom Spark configurations
COPY spark/config/spark-defaults.conf ${SPARK_HOME}/conf/spark-defaults.conf
COPY spark/config/log4j.properties ${SPARK_HOME}/conf/log4j.properties

# Copy Spark jobs and libraries
COPY spark/jobs ${SPARK_HOME}/jobs
COPY spark/lib ${SPARK_HOME}/lib

# Note: Additional JARs can be added to docker/spark/jars/ directory if needed

WORKDIR ${SPARK_HOME}
