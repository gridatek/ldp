FROM python:3.14-slim

# Create airflow user and group
RUN groupadd -r airflow && \
    useradd -r -g airflow -u 50000 -d /opt/airflow -s /bin/bash airflow

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create airflow directories
RUN mkdir -p /opt/airflow/dags /opt/airflow/logs /opt/airflow/plugins && \
    chown -R airflow:root /opt/airflow && \
    chmod -R 775 /opt/airflow

# Install Apache Airflow
# Using constraints file for Python 3.13 as 3.14 constraints may not exist yet
RUN pip install --no-cache-dir "apache-airflow==3.0.2" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.0.2/constraints-3.13.txt" || \
    pip install --no-cache-dir "apache-airflow==3.0.2" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.0.2/constraints-no-providers-3.13.txt" || \
    pip install --no-cache-dir "apache-airflow==3.0.2"

USER airflow
WORKDIR /opt/airflow

# Install Python dependencies
COPY docker/airflow/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy DAGs and plugins (if they exist)
COPY --chown=airflow:root airflow/dags /opt/airflow/dags
COPY --chown=airflow:root airflow/plugins /opt/airflow/plugins

# Set environment variables
ENV AIRFLOW_HOME=/opt/airflow
ENV PYTHONPATH=/opt/airflow
