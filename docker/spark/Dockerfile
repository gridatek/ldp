FROM apache/spark:3.5.0-python3

USER root

# Install Python packages
RUN pip install --no-cache-dir \
    pyspark==3.5.0 \
    pandas==2.1.4 \
    numpy==1.26.3 \
    pyarrow==14.0.2 \
    boto3==1.34.21 \
    s3fs==2024.2.0

# Copy custom Spark configurations
COPY spark/config/spark-defaults.conf /opt/spark/conf/spark-defaults.conf
COPY spark/config/log4j.properties /opt/spark/conf/log4j.properties

# Copy Spark jobs and libraries
COPY spark/jobs /opt/spark/jobs
COPY spark/lib /opt/spark/lib

# Note: Additional JARs can be added to docker/spark/jars/ directory if needed

WORKDIR /opt/spark
