FROM apache/airflow:2.7.3-python3.11

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy DAGs and plugins (if they exist)
COPY --chown=airflow:root airflow/dags /opt/airflow/dags
COPY --chown=airflow:root airflow/plugins /opt/airflow/plugins
