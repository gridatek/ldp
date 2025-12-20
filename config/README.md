# Config Directory

This directory contains configuration files for all LDP services.

## Structure

```
config/
├── iceberg/
│   └── catalog.properties    # Iceberg catalog configuration
└── README.md                 # This file
```

## Configuration Files

### Iceberg Configuration

**File**: `iceberg/catalog.properties`

Configures the Apache Iceberg table format:

```properties
# Catalog type - using HadoopCatalog (file-based)
catalog-impl=org.apache.iceberg.hadoop.HadoopCatalog

# Warehouse location - where Iceberg tables are stored
warehouse=s3a://warehouse/

# S3/MinIO Configuration
s3.endpoint=http://minio:9000
s3.access-key-id=admin
s3.secret-access-key=minioadmin
s3.path-style-access=true

# File format settings
write.format.default=parquet
write.parquet.compression-codec=snappy

# Metadata settings
commit.retry.num-retries=3
commit.retry.min-wait-ms=100
```

**Key Settings:**

- **`catalog-impl`**: Uses HadoopCatalog (file-based, no external metastore)
- **`warehouse`**: All Iceberg tables stored in MinIO's `warehouse` bucket
- **`s3.endpoint`**: Points to MinIO service
- **`s3.path-style-access=true`**: Required for MinIO compatibility

## Understanding Iceberg Catalog

The HadoopCatalog is a simple, file-based catalog suitable for development and small deployments.

**Pros:**
- No external metastore needed
- Simple setup
- Works well with object storage (MinIO/S3)

**Cons:**
- Limited concurrency
- Not recommended for production multi-user environments

**Learn more:**
- `docs/iceberg-hadoop-catalog.md` - Detailed explanation
- `docs/hive-vs-iceberg.md` - Why we use Iceberg

## Environment-Specific Configuration

For different environments (dev, staging, prod), you can:

1. Create environment-specific config files:
   ```
   config/iceberg/
   ├── catalog.dev.properties
   ├── catalog.staging.properties
   └── catalog.prod.properties
   ```

2. Use environment variables in your Spark configurations to switch between them

## Adding New Configurations

When adding new services or configuration files:

1. Create a subdirectory: `config/service_name/`
2. Add configuration files
3. Update this README
4. Document in service README

## Service Configuration Locations

Some services have configuration embedded in other locations:

- **Airflow**: Environment variables in `docker-compose.yml`
- **Spark**: Configuration in Spark session creation (see `examples/iceberg_crud.py`)
- **MinIO**: Environment variables in `docker-compose.yml`
- **PostgreSQL**: Environment variables in `docker-compose.yml`

## Security Note

**⚠️ Important**: The current configuration uses default credentials suitable for local development only.

**For production:**
- Use strong passwords
- Store credentials in secrets management (AWS Secrets Manager, HashiCorp Vault)
- Never commit production credentials to git
- Use environment variables or secret files

## Learn More

- Iceberg Configuration: https://iceberg.apache.org/docs/latest/configuration/
- Getting Started: `docs/getting-started-tutorial.md`
- Production Setup: `docs/production-guide.md`
