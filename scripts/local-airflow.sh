#!/bin/bash

# Local Airflow Standalone Development Setup
# This script runs Airflow in standalone mode without Docker/Kubernetes
# Requires only Python 3.11+

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
AIRFLOW_HOME="${PROJECT_ROOT}/.airflow-local"
AIRFLOW_VERSION="2.10.4"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_python() {
    log_info "Checking Python installation..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.11+"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    log_success "Found Python ${PYTHON_VERSION}"

    # Check minimum version (3.8+)
    MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 8 ]); then
        log_error "Python 3.8+ is required. Found ${PYTHON_VERSION}"
        exit 1
    fi
}

setup_venv() {
    log_info "Setting up virtual environment..."

    VENV_DIR="${PROJECT_ROOT}/.venv-airflow"

    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        log_success "Created virtual environment at $VENV_DIR"
    else
        log_info "Virtual environment already exists"
    fi

    # Activate virtual environment
    source "${VENV_DIR}/bin/activate"

    # Upgrade pip
    pip install --upgrade pip > /dev/null 2>&1
}

install_airflow() {
    log_info "Installing Apache Airflow ${AIRFLOW_VERSION}..."

    # Check if Airflow is already installed
    if pip show apache-airflow > /dev/null 2>&1; then
        INSTALLED_VERSION=$(pip show apache-airflow | grep Version | cut -d: -f2 | tr -d ' ')
        log_info "Airflow ${INSTALLED_VERSION} is already installed"
        return
    fi

    # Set constraint URL for reproducible installs
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

    log_info "Using constraints from: ${CONSTRAINT_URL}"

    # Install Airflow with common extras
    pip install "apache-airflow==${AIRFLOW_VERSION}" \
        --constraint "${CONSTRAINT_URL}"

    # Install additional providers from project requirements
    log_info "Installing additional dependencies..."
    pip install \
        pandas \
        numpy \
        pyarrow \
        psycopg2-binary \
        boto3 \
        s3fs \
        pyyaml \
        python-dotenv

    log_success "Airflow ${AIRFLOW_VERSION} installed successfully"
}

configure_airflow() {
    log_info "Configuring Airflow..."

    export AIRFLOW_HOME

    # Create Airflow home directory
    mkdir -p "$AIRFLOW_HOME"

    # Initialize the database if not exists
    if [ ! -f "${AIRFLOW_HOME}/airflow.db" ]; then
        log_info "Initializing Airflow database..."
        airflow db init
    fi

    # Create symlink to DAGs
    DAGS_LINK="${AIRFLOW_HOME}/dags"
    PROJECT_DAGS="${PROJECT_ROOT}/airflow/dags"

    if [ -L "$DAGS_LINK" ]; then
        rm "$DAGS_LINK"
    elif [ -d "$DAGS_LINK" ]; then
        rm -rf "$DAGS_LINK"
    fi

    ln -s "$PROJECT_DAGS" "$DAGS_LINK"
    log_success "Linked DAGs directory: $PROJECT_DAGS -> $DAGS_LINK"

    # Create symlink to plugins
    PLUGINS_LINK="${AIRFLOW_HOME}/plugins"
    PROJECT_PLUGINS="${PROJECT_ROOT}/airflow/plugins"

    if [ -L "$PLUGINS_LINK" ]; then
        rm "$PLUGINS_LINK"
    elif [ -d "$PLUGINS_LINK" ]; then
        rm -rf "$PLUGINS_LINK"
    fi

    if [ -d "$PROJECT_PLUGINS" ]; then
        ln -s "$PROJECT_PLUGINS" "$PLUGINS_LINK"
        log_success "Linked plugins directory: $PROJECT_PLUGINS -> $PLUGINS_LINK"
    fi

    # Set configuration
    log_info "Updating Airflow configuration..."

    # Create/update airflow.cfg with local development settings
    if [ -f "${AIRFLOW_HOME}/airflow.cfg" ]; then
        # Update existing config for local development
        sed -i 's/^load_examples = .*/load_examples = False/' "${AIRFLOW_HOME}/airflow.cfg" 2>/dev/null || true
        sed -i 's/^executor = .*/executor = SequentialExecutor/' "${AIRFLOW_HOME}/airflow.cfg" 2>/dev/null || true
        sed -i 's/^dags_are_paused_at_creation = .*/dags_are_paused_at_creation = False/' "${AIRFLOW_HOME}/airflow.cfg" 2>/dev/null || true
    fi

    log_success "Airflow configured for local development"
}

create_admin_user() {
    log_info "Creating admin user..."

    export AIRFLOW_HOME

    # Check if admin user exists
    if airflow users list 2>/dev/null | grep -q "admin"; then
        log_info "Admin user already exists"
        return
    fi

    # Create admin user
    airflow users create \
        --username admin \
        --password admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com

    log_success "Admin user created (username: admin, password: admin)"
}

start_standalone() {
    log_info "Starting Airflow in standalone mode..."

    export AIRFLOW_HOME
    export AIRFLOW__CORE__LOAD_EXAMPLES=False
    export AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=False
    export AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True
    export AIRFLOW__WEBSERVER__WARN_DEPLOYMENT_EXPOSURE=False

    echo ""
    echo "=============================================="
    echo -e "${GREEN}  Airflow Local Development Server${NC}"
    echo "=============================================="
    echo ""
    echo "  Web UI:      http://localhost:8080"
    echo "  Username:    admin"
    echo "  Password:    admin"
    echo ""
    echo "  DAGs folder: ${PROJECT_ROOT}/airflow/dags"
    echo "  AIRFLOW_HOME: ${AIRFLOW_HOME}"
    echo ""
    echo "  Press Ctrl+C to stop"
    echo "=============================================="
    echo ""

    # Start Airflow standalone (webserver + scheduler + triggerer)
    airflow standalone
}

stop_airflow() {
    log_info "Stopping Airflow processes..."

    # Kill airflow processes
    pkill -f "airflow webserver" 2>/dev/null || true
    pkill -f "airflow scheduler" 2>/dev/null || true
    pkill -f "airflow triggerer" 2>/dev/null || true

    log_success "Airflow processes stopped"
}

reset_airflow() {
    log_warning "This will delete all local Airflow data!"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        stop_airflow
        rm -rf "${PROJECT_ROOT}/.airflow-local"
        rm -rf "${PROJECT_ROOT}/.venv-airflow"
        log_success "Airflow local data reset"
    else
        log_info "Reset cancelled"
    fi
}

show_help() {
    echo "Local Airflow Development Setup"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     Setup and start Airflow standalone (default)"
    echo "  stop      Stop running Airflow processes"
    echo "  reset     Delete all local Airflow data and start fresh"
    echo "  status    Check if Airflow is running"
    echo "  help      Show this help message"
    echo ""
    echo "Environment:"
    echo "  AIRFLOW_HOME: ${AIRFLOW_HOME}"
    echo "  VENV: ${PROJECT_ROOT}/.venv-airflow"
    echo ""
}

status_check() {
    if pgrep -f "airflow webserver" > /dev/null 2>&1; then
        log_success "Airflow webserver is running"
    else
        log_warning "Airflow webserver is not running"
    fi

    if pgrep -f "airflow scheduler" > /dev/null 2>&1; then
        log_success "Airflow scheduler is running"
    else
        log_warning "Airflow scheduler is not running"
    fi
}

# Main entry point
case "${1:-start}" in
    start)
        check_python
        setup_venv
        install_airflow
        configure_airflow
        create_admin_user
        start_standalone
        ;;
    stop)
        stop_airflow
        ;;
    reset)
        reset_airflow
        ;;
    status)
        status_check
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
