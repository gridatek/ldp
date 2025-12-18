# CI/CD Testing

LDP uses GitHub Actions for continuous integration testing across all supported platforms.

## Workflows

### 1. CI Testing (`ci.yml`)

Main integration testing workflow for the platform.

**Triggers**: Push to main, Pull requests, Manual dispatch

**Jobs**:
- **Terraform Validation** - Format, init, validate across all environments
- **Python Linting & Testing** - Flake8, black, pylint, pytest
- **Shell Script Validation** - ShellCheck for bash scripts
- **YAML Validation** - yamllint for Kubernetes manifests
- **Docker Build Tests** - Build all service images (Airflow, Spark, Jupyter)
- **Documentation Check** - Validate README and docs
- **Security Scan** - Trivy vulnerability scanner, TruffleHog secrets detection
- **Project Structure** - Verify required directories and files
- **Cluster Integration Test** - Full E2E deployment on Minikube
  - Deploy infrastructure with Terraform (20min timeout)
  - Initialize MinIO buckets
  - Upload test data
  - Verify all pods running
  - Test complete data pipeline

**Runner**: `ubuntu-latest`

### 2. Platform Tests (`platform-tests.yml`)

Cross-platform compatibility testing.

**Triggers**: Push to main, Pull requests, Manual dispatch

**Jobs**:

#### Windows Integration Tests
- **Runner**: `windows-latest`
- PowerShell script syntax validation
- Terraform validation on Windows
- Python linting
- Prerequisite checking

#### macOS Integration Tests
- **Runner**: `macos-latest`
- Bash script syntax validation
- Platform detection testing
- Terraform validation on macOS
- Python linting and syntax checks

#### Linux Integration Tests
- **Runner**: `ubuntu-latest`
- Bash script syntax validation
- Platform detection testing
- Terraform validation on Linux
- Python linting and unit tests
- Full dependency installation

#### E2E Tests (Linux)
- **Runner**: `ubuntu-latest`
- **Depends on**: linux-integration-tests
- **Timeout**: 15 minutes
- Full Minikube deployment
- Platform health verification
- Automatic cleanup

#### Documentation Validation
- **Runner**: `ubuntu-latest`
- Platform guide existence
- Internal link checking
- Markdown structure validation

#### Platform Summary
- Aggregates all test results
- Provides unified pass/fail status

## Test Coverage

### What Gets Tested

**Script Validation**:
- ✅ Bash scripts (Linux, macOS)
- ✅ PowerShell scripts (Windows)
- ✅ ShellCheck for bash
- ✅ Syntax validation

**Infrastructure**:
- ✅ Terraform format, init, validate (all platforms)
- ✅ Kubernetes manifests (YAML)
- ✅ Docker image builds
- ✅ Helm chart validation

**Code Quality**:
- ✅ Python linting (flake8)
- ✅ Python formatting (black)
- ✅ Python complexity (pylint)
- ✅ Python unit tests (pytest)

**Security**:
- ✅ Vulnerability scanning (Trivy)
- ✅ Secret detection (TruffleHog)

**End-to-End**:
- ✅ Full platform deployment
- ✅ Service health checks
- ✅ Data pipeline testing
- ✅ MinIO operations

## Platform-Specific Tests

### Windows (`windows-latest`)
- PowerShell script syntax
- Terraform compatibility
- Python tooling

### macOS (`macos-latest`)
- Bash script syntax
- Platform detection
- Homebrew compatibility
- Apple Silicon support

### Linux (`ubuntu-latest`)
- Bash script syntax
- Full E2E deployment
- Minikube integration
- Complete data pipeline

## Running Tests Locally

### Python Tests
```bash
# Install dependencies
pip install pytest pylint flake8 black

# Run linting
flake8 airflow/ spark/ tests/ examples/ \
  --count --select=E9,F63,F7,F82 --show-source --statistics

# Run unit tests
pytest airflow/tests/ -v
pytest spark/tests/ -v
```

### Terraform Tests
```bash
cd terraform

# Format check
terraform fmt -check -recursive

# Validate
terraform init -backend=false
terraform validate
```

### Script Tests
```bash
# Bash syntax check
bash -n scripts/setup.sh

# ShellCheck
shellcheck scripts/*.sh
```

### YAML Tests
```bash
# Install yamllint
pip install yamllint

# Lint Kubernetes manifests
yamllint kubernetes/

# Lint workflows
yamllint .github/workflows/
```

## CI Configuration

### Terraform Timeout
```yaml
timeout-minutes: 20  # For deployment
```

### Minikube Configuration
```yaml
cpus: 2
memory: 4096
kubernetes-version: 1.34.0
```

### Python Version
```yaml
python-version: '3.11'
```

## Troubleshooting CI Failures

### Terraform Validation Fails
- Check `terraform fmt` output
- Verify `local.tfvars` exists
- Ensure all modules are valid

### Python Linting Fails
- Check `.flake8` configuration
- Fix syntax errors (E9 codes)
- Resolve undefined names (F821)

### E2E Tests Timeout
- Check pod status in logs
- Verify Minikube started correctly
- Review Terraform apply logs

### Platform Tests Fail
- Windows: Check PowerShell syntax
- macOS: Verify bash compatibility
- Linux: Check script permissions

## Best Practices

1. **Run tests locally** before pushing
2. **Check CI status** before merging
3. **Review failed logs** in GitHub Actions
4. **Keep scripts portable** across platforms
5. **Use standard Python** (no platform-specific imports)
6. **Document platform-specific** behavior

## Status Badges

Add to your PR description:
```markdown
[![CI Testing](https://github.com/gridatek/ldp/actions/workflows/ci.yml/badge.svg?branch=your-branch)](https://github.com/gridatek/ldp/actions/workflows/ci.yml)
[![Platform Tests](https://github.com/gridatek/ldp/actions/workflows/platform-tests.yml/badge.svg?branch=your-branch)](https://github.com/gridatek/ldp/actions/workflows/platform-tests.yml)
```

## Contributing

When adding new code:
- ✅ Add appropriate tests
- ✅ Ensure cross-platform compatibility
- ✅ Update CI if adding new platforms
- ✅ Document platform-specific requirements
