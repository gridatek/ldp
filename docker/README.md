# Docker Directory

This directory contains Dockerfiles and requirements files for building custom Docker images used in LDP.

## Structure

```
docker/
├── airflow/
│   ├── Dockerfile           # Custom Airflow image
│   └── requirements.txt     # Python packages for Airflow
├── jupyter/
│   ├── Dockerfile           # Jupyter Lab image with Spark + Iceberg
│   └── requirements.txt     # Python packages for Jupyter
├── spark/
│   ├── Dockerfile           # Custom Spark image
│   └── requirements.txt     # Python packages for Spark workers
└── README.md                # This file
```

## Docker Images

### Airflow Image

**Base**: `apache/airflow:3.1.5-python3.13`

**Custom additions:**
- AWS provider for MinIO integration
- Spark provider for Spark job submission
- Additional data processing libraries (pandas, numpy, pyarrow)

**Build:**
```bash
docker-compose build airflow
```

**Modify dependencies:**
Edit `docker/airflow/requirements.txt` and rebuild.

### Spark Image

**Base**: `apache/spark:4.0.1-python3`

**Custom additions:**
- PySpark 4.0.1
- Data processing libraries (pandas, numpy, pyarrow)
- S3/MinIO support (boto3, s3fs)
- PyIceberg for Iceberg table operations

**Build:**
```bash
docker-compose build spark-master spark-worker
```

**Modify dependencies:**
Edit `docker/spark/requirements.txt` and rebuild.

### Jupyter Image

**Base**: `jupyter/pyspark-notebook`

**Custom additions:**
- JupyterLab for interactive development
- PySpark 4.0.1 with Iceberg support
- Data science libraries (pandas, matplotlib, seaborn, plotly)
- Database connectivity (SQLAlchemy, psycopg2)

**Build:**
```bash
docker-compose build jupyter
```

**Access Jupyter:**
- URL: http://localhost:8888
- Token: Check logs with `docker logs ldp-jupyter`

**Modify dependencies:**
Edit `docker/jupyter/requirements.txt` and rebuild.

## Requirements Files

### Pinned Versions

All `requirements.txt` files use **pinned versions** to ensure reproducibility:

```txt
# Good (pinned)
pandas==2.3.3
numpy==2.3.5

# Avoid (unpinned)
pandas>=2.0.0
numpy
```

**Why pin versions?**
- Reproducible builds
- Avoid breaking changes
- Easier debugging

### Recent Version Updates

The project has been upgraded to modern versions:
- **Python**: 3.13
- **Airflow**: 3.1.5
- **PySpark**: 4.0.1
- **NumPy**: 2.3.5
- **Pandas**: 2.3.3
- **PyArrow**: 22.0.0

See `docs/UPGRADE-PLAN-2025.md` for migration details.

## Adding New Dependencies

### For Airflow

1. Edit `docker/airflow/requirements.txt`
2. Add the package with pinned version:
   ```txt
   my-package==1.2.3
   ```
3. Rebuild and restart:
   ```bash
   docker-compose build airflow
   docker-compose up -d airflow-webserver airflow-scheduler
   ```

### For Spark

1. Edit `docker/spark/requirements.txt`
2. Add the package
3. Rebuild all Spark services:
   ```bash
   docker-compose build spark-master spark-worker
   docker-compose up -d spark-master spark-worker
   ```

### For Jupyter

1. Edit `docker/jupyter/requirements.txt`
2. Add the package
3. Rebuild:
   ```bash
   docker-compose build jupyter
   docker-compose up -d jupyter
   ```

## Dockerfile Best Practices

### 1. Use Official Base Images
All our Dockerfiles use official images from Apache and Jupyter.

### 2. Pin Package Versions
Always specify exact versions in `requirements.txt`.

### 3. Layer Caching
Requirements are copied before other files to leverage Docker layer caching:
```dockerfile
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
# Other files copied after
```

### 4. Security
- Run as non-root user where possible
- Keep base images updated
- Scan for vulnerabilities: `docker scan image-name`

## Common Issues

### Build Failures

**Dependency conflicts:**
```bash
# Clear Docker cache and rebuild
docker-compose build --no-cache service-name
```

**Version not found:**
- Check if the version exists on PyPI
- See recent fix for fsspec/s3fs version pinning

### Image Size Too Large

- Use `.dockerignore` to exclude unnecessary files
- Combine RUN commands to reduce layers
- Use multi-stage builds if needed

## Rebuilding All Images

To rebuild all services:

```bash
# Stop services
make down

# Rebuild all images
docker-compose build

# Start services
make up
```

## Image Management

```bash
# List images
docker images | grep ldp

# Remove unused images
docker image prune

# Remove all LDP images (careful!)
docker-compose down --rmi all
```

## Learn More

- Dockerfile reference: https://docs.docker.com/engine/reference/builder/
- Docker Compose: https://docs.docker.com/compose/
- Getting Started: `docs/getting-started-tutorial.md`
