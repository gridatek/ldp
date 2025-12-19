FROM apache/spark:4.0.1-python3

USER root

# Install Python packages (use versions compatible with the base image)
RUN pip install --no-cache-dir \
    boto3 \
    s3fs

# Copy custom Spark configurations
COPY spark/config/spark-defaults.conf /opt/spark/conf/spark-defaults.conf
COPY spark/config/log4j.properties /opt/spark/conf/log4j.properties

# Copy Spark jobs and libraries
COPY spark/jobs /opt/spark/jobs
COPY spark/lib /opt/spark/lib

# Note: Additional JARs can be added to docker/spark/jars/ directory if needed

WORKDIR /opt/spark
