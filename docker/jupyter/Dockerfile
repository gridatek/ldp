FROM python:3.14-slim

# Create jovyan user (standard Jupyter user)
RUN groupadd -r jovyan -g 1000 && \
    useradd -r -g jovyan -u 1000 -d /home/jovyan -s /bin/bash -m jovyan

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    vim \
    wget \
    git \
    openjdk-17-jdk-headless \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up Java environment for Spark
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# Create necessary directories
RUN mkdir -p /home/jovyan/work /home/jovyan/notebooks && \
    chown -R jovyan:jovyan /home/jovyan

USER jovyan
WORKDIR /home/jovyan

# Install Python packages
COPY docker/jupyter/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy notebooks (if they exist)
# COPY spark/notebooks /home/jovyan/notebooks

# Set Spark configurations
ENV SPARK_MASTER=spark://spark-master-svc:7077
ENV PYSPARK_SUBMIT_ARGS="--packages org.apache.iceberg:iceberg-spark-runtime-4.0_2.13:1.10.0,org.apache.hadoop:hadoop-aws:3.4.1 pyspark-shell"
ENV NB_UID=1000
ENV NB_GID=1000

# Expose JupyterLab port
EXPOSE 8888

# Start JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
