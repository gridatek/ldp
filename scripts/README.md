# Scripts Directory

This directory contains utility scripts for managing and operating the LDP platform.

## Structure

```
scripts/
├── init/              # Initialization scripts
├── setup/             # Setup and configuration scripts
├── validation/        # Validation and health check scripts
└── README.md          # This file
```

## Purpose

Scripts in this directory are used for:

- **Platform initialization** - Setting up services on first run
- **Health checks** - Verifying services are running correctly
- **Data seeding** - Loading initial or test data
- **Maintenance** - Cleanup, backups, and other operations
- **Validation** - Checking configurations and dependencies

## Using Scripts

### Running Scripts

Most scripts are designed to be run from the project root:

```bash
# Example
./scripts/init/setup_minio.sh
```

Or via Make targets (recommended):

```bash
# Make wraps scripts with proper error handling
make init
make validate
```

## Common Script Categories

### Initialization Scripts

**Purpose**: Set up services and create required resources on first deployment

**Examples:**
- Create MinIO buckets
- Initialize Iceberg warehouse
- Set up Airflow connections
- Create database schemas

**When to run**: First deployment or after `make clean`

### Validation Scripts

**Purpose**: Verify platform health and configuration

**Examples:**
- Check service connectivity
- Validate configuration files
- Verify required buckets/tables exist
- Test authentication

**When to run**: After deployment, before production use, in CI/CD

### Maintenance Scripts

**Purpose**: Ongoing platform maintenance

**Examples:**
- Clean up old logs
- Compact Iceberg tables
- Backup metadata
- Rotate credentials

**When to run**: Scheduled (cron) or as needed

## Best Practices for Scripts

### 1. Make Scripts Idempotent

Scripts should be safe to run multiple times:

```bash
# Good - check before creating
if ! bucket_exists "my-bucket"; then
    create_bucket "my-bucket"
fi

# Bad - fails on second run
create_bucket "my-bucket"
```

### 2. Add Error Handling

Always check for errors:

```bash
#!/bin/bash
set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Your script here
```

### 3. Use Logging

Add informative logging:

```bash
echo "[INFO] Starting initialization..."
echo "[SUCCESS] Bucket created: datalake"
echo "[ERROR] Failed to connect to MinIO" >&2
```

### 4. Document Parameters

If script takes arguments, document them:

```bash
#!/bin/bash
# Usage: ./script.sh <environment> <region>
# Example: ./script.sh prod us-east-1

if [ $# -ne 2 ]; then
    echo "Usage: $0 <environment> <region>"
    exit 1
fi
```

### 5. Make Scripts Executable

```bash
chmod +x scripts/your_script.sh
```

## Integration with Makefile

Many scripts are wrapped in Makefile targets for ease of use:

```makefile
# In Makefile
.PHONY: init
init:
	@./scripts/init/setup_platform.sh
```

**Benefits:**
- Consistent interface (`make init`)
- Error handling
- Documentation (`make help`)
- Dependencies between targets

## Creating New Scripts

When adding a new script:

1. **Choose the right directory**:
   - Initialization? → `scripts/init/`
   - Validation? → `scripts/validation/`
   - Other? → Appropriate subdirectory

2. **Follow naming conventions**:
   - Use descriptive names: `setup_minio_buckets.sh`
   - Use underscores, not hyphens: `check_services.sh`

3. **Add a header**:
   ```bash
   #!/bin/bash
   # Description: What this script does
   # Usage: How to run it
   # Author: Your name
   ```

4. **Make it executable**:
   ```bash
   chmod +x scripts/your_script.sh
   ```

5. **Test thoroughly**:
   - Test on clean environment
   - Test idempotency (run twice)
   - Test error cases

6. **Document in README**:
   - Add to this file
   - Update main README if needed
   - Add to Makefile help if appropriate

7. **Add to version control**:
   ```bash
   git add scripts/your_script.sh
   ```

## Script Templates

### Basic Bash Script

```bash
#!/bin/bash
set -euo pipefail

# Description of what this script does
# Usage: ./script_name.sh [args]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Main script logic
main() {
    log_info "Starting script..."

    # Your logic here

    log_info "Script completed successfully"
}

# Run main function
main "$@"
```

### Python Script

```python
#!/usr/bin/env python3
"""
Description: What this script does
Usage: python script_name.py [args]
"""
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main script logic."""
    logger.info("Starting script...")

    try:
        # Your logic here
        pass
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)

    logger.info("Script completed successfully")


if __name__ == "__main__":
    main()
```

## Common Operations

### Check Service Health

```bash
#!/bin/bash
# Check if all services are healthy

services=("airflow" "spark-master" "minio" "postgres")

for service in "${services[@]}"; do
    if docker ps | grep -q "$service"; then
        echo "✓ $service is running"
    else
        echo "✗ $service is NOT running"
        exit 1
    fi
done
```

### Create MinIO Bucket

```bash
#!/bin/bash
# Create MinIO bucket if it doesn't exist

BUCKET_NAME="${1:-datalake}"

# Using mc (MinIO Client)
mc alias set minio http://localhost:9000 admin minioadmin

if mc ls minio/$BUCKET_NAME >/dev/null 2>&1; then
    echo "Bucket $BUCKET_NAME already exists"
else
    mc mb minio/$BUCKET_NAME
    echo "Created bucket $BUCKET_NAME"
fi
```

### Validate Configuration

```bash
#!/bin/bash
# Validate Iceberg configuration

CONFIG_FILE="config/iceberg/catalog.properties"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Configuration file not found: $CONFIG_FILE"
    exit 1
fi

# Check required properties
required_props=("catalog-impl" "warehouse" "s3.endpoint")

for prop in "${required_props[@]}"; do
    if ! grep -q "^$prop=" "$CONFIG_FILE"; then
        echo "ERROR: Missing required property: $prop"
        exit 1
    fi
done

echo "Configuration validated successfully"
```

## Security Considerations

### Handling Secrets

**Never hardcode secrets in scripts:**

```bash
# Bad
PASSWORD="secret123"

# Good - use environment variables
PASSWORD="${MINIO_PASSWORD:-}"

# Good - read from secrets file
PASSWORD=$(cat /run/secrets/minio_password)

# Good - prompt user
read -s -p "Enter password: " PASSWORD
```

### File Permissions

Protect sensitive scripts:

```bash
# Make script readable/executable only by owner
chmod 700 scripts/sensitive_script.sh

# Or for group access
chmod 750 scripts/sensitive_script.sh
```

## Troubleshooting

### Permission Denied

```bash
# Make script executable
chmod +x scripts/your_script.sh
```

### Command Not Found

```bash
# Check if command is installed
which python3
which docker

# Install if missing
apt-get install python3
```

### Script Fails in CI/CD

- Test locally first
- Check for environment-specific assumptions
- Use relative paths, not absolute
- Verify all dependencies are available

## Learn More

- Bash scripting guide: https://www.gnu.org/software/bash/manual/
- Shell script best practices: https://google.github.io/styleguide/shellguide.html
- Makefile documentation: See `Makefile` in project root
