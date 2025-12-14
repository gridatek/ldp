FROM jupyter/pyspark-notebook:latest

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

# Install Python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy notebooks
COPY notebooks /home/jovyan/notebooks

# Set Spark configurations
ENV SPARK_MASTER=spark://spark-master-svc:7077
ENV PYSPARK_SUBMIT_ARGS="--packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3,org.apache.hadoop:hadoop-aws:3.3.4 pyspark-shell"

WORKDIR /home/jovyan
