#!/bin/bash
# Interactive troubleshooting script for Local Data Platform
# Usage: ./scripts/troubleshoot.sh [--full|--export-logs|--quick]

set -e

NAMESPACE="ldp"
LOG_DIR="./logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_status() {
    if [ "$2" = "ok" ]; then
        echo -e "${GREEN}[OK]${NC} $1"
    elif [ "$2" = "warn" ]; then
        echo -e "${YELLOW}[WARN]${NC} $1"
    elif [ "$2" = "error" ]; then
        echo -e "${RED}[ERROR]${NC} $1"
    else
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Check kubectl
    if command -v kubectl &> /dev/null; then
        print_status "kubectl installed" "ok"
    else
        print_status "kubectl not found" "error"
        exit 1
    fi

    # Check minikube
    if command -v minikube &> /dev/null; then
        print_status "minikube installed" "ok"
    else
        print_status "minikube not found" "error"
        exit 1
    fi

    # Check minikube running
    if minikube status | grep -q "Running"; then
        print_status "minikube is running" "ok"
    else
        print_status "minikube is not running" "error"
        echo "  Run: minikube start --memory=8192 --cpus=4"
        exit 1
    fi

    # Check namespace exists
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        print_status "Namespace '$NAMESPACE' exists" "ok"
    else
        print_status "Namespace '$NAMESPACE' does not exist" "error"
        echo "  Run: make start"
        exit 1
    fi
}

check_pods() {
    print_header "Pod Status"

    echo ""
    kubectl get pods -n "$NAMESPACE" -o wide
    echo ""

    # Count pods by status
    TOTAL=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
    RUNNING=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
    PENDING=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Pending --no-headers 2>/dev/null | wc -l)
    FAILED=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Failed --no-headers 2>/dev/null | wc -l)

    print_status "Total pods: $TOTAL"

    if [ "$RUNNING" -eq "$TOTAL" ]; then
        print_status "All $RUNNING pods running" "ok"
    else
        print_status "Running: $RUNNING, Pending: $PENDING, Failed: $FAILED" "warn"
    fi

    # Check for pods in bad state
    BAD_PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -E "CrashLoopBackOff|Error|ImagePullBackOff|Pending" || true)
    if [ -n "$BAD_PODS" ]; then
        echo ""
        print_status "Pods with issues:" "warn"
        echo "$BAD_PODS"
    fi
}

check_services() {
    print_header "Services & Endpoints"

    echo ""
    echo "Services:"
    kubectl get svc -n "$NAMESPACE"

    echo ""
    echo "Endpoints:"
    kubectl get endpoints -n "$NAMESPACE" | grep -v "none" || echo "No endpoints with targets found"
}

check_pvcs() {
    print_header "Persistent Volume Claims"

    echo ""
    kubectl get pvc -n "$NAMESPACE"

    # Check for unbound PVCs
    UNBOUND=$(kubectl get pvc -n "$NAMESPACE" --no-headers 2>/dev/null | grep -v "Bound" || true)
    if [ -n "$UNBOUND" ]; then
        echo ""
        print_status "Unbound PVCs found:" "warn"
        echo "$UNBOUND"
    else
        print_status "All PVCs are bound" "ok"
    fi
}

check_resources() {
    print_header "Resource Usage"

    echo ""
    echo "Node Resources:"
    kubectl top nodes 2>/dev/null || echo "Metrics server not available"

    echo ""
    echo "Pod Resources:"
    kubectl top pods -n "$NAMESPACE" 2>/dev/null || echo "Pod metrics not available"

    echo ""
    echo "Minikube Resources:"
    minikube ssh "echo 'Memory:' && free -h | head -2 && echo '' && echo 'Disk:' && df -h / | head -2" 2>/dev/null || echo "Could not check minikube resources"
}

check_events() {
    print_header "Recent Events (last 20)"

    echo ""
    kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' 2>/dev/null | tail -20 || echo "No events found"
}

check_component() {
    local _component=$1
    local label=$2
    local name=$3

    echo ""
    echo -e "${BLUE}--- $name ---${NC}"

    POD_STATUS=$(kubectl get pods -n "$NAMESPACE" -l "$label" --no-headers 2>/dev/null | head -1)
    if [ -n "$POD_STATUS" ]; then
        POD_NAME=$(echo "$POD_STATUS" | awk '{print $1}')
        STATUS=$(echo "$POD_STATUS" | awk '{print $3}')
        RESTARTS=$(echo "$POD_STATUS" | awk '{print $4}')

        if [ "$STATUS" = "Running" ]; then
            print_status "$name is running (restarts: $RESTARTS)" "ok"
        else
            print_status "$name status: $STATUS" "error"
        fi

        # Show recent logs if not running
        if [ "$STATUS" != "Running" ]; then
            echo "Recent logs:"
            kubectl logs -n "$NAMESPACE" "$POD_NAME" --tail=10 2>/dev/null || echo "Could not get logs"
        fi
    else
        print_status "$name pod not found" "error"
    fi
}

check_components() {
    print_header "Component Health"

    check_component "airflow" "component=webserver" "Airflow Webserver"
    check_component "airflow" "component=scheduler" "Airflow Scheduler"
    check_component "spark" "app=spark-master" "Spark Master"
    check_component "spark" "app=spark-worker" "Spark Worker"
    check_component "minio" "app=minio" "MinIO"
    check_component "postgresql" "app=postgresql" "PostgreSQL"
    check_component "prometheus" "app=prometheus" "Prometheus"
    check_component "grafana" "app=grafana" "Grafana"
}

check_connectivity() {
    print_header "Network Connectivity"

    # Get a running pod to test from
    TEST_POD=$(kubectl get pods -n "$NAMESPACE" -l app=minio --no-headers 2>/dev/null | awk '{print $1}' | head -1)

    if [ -z "$TEST_POD" ]; then
        print_status "No pods available to test connectivity" "warn"
        return
    fi

    echo "Testing DNS resolution from $TEST_POD:"

    for svc in "minio" "spark-master" "postgresql" "prometheus"; do
        if kubectl exec -n "$NAMESPACE" "$TEST_POD" -- nslookup "$svc" &>/dev/null; then
            print_status "DNS: $svc" "ok"
        else
            print_status "DNS: $svc - resolution failed" "error"
        fi
    done
}

export_logs() {
    print_header "Exporting Logs"

    mkdir -p "$LOG_DIR/$TIMESTAMP"

    echo "Exporting to $LOG_DIR/$TIMESTAMP/"

    # Export pod descriptions
    kubectl get pods -n "$NAMESPACE" -o yaml > "$LOG_DIR/$TIMESTAMP/pods.yaml" 2>/dev/null
    print_status "Pod descriptions exported" "ok"

    # Export events
    kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' > "$LOG_DIR/$TIMESTAMP/events.txt" 2>/dev/null
    print_status "Events exported" "ok"

    # Export logs for each component
    for label in "component=webserver" "component=scheduler" "app=spark-master" "app=spark-worker" "app=minio" "app=postgresql"; do
        COMPONENT_NAME=$(echo "$label" | cut -d'=' -f2)
        kubectl logs -n "$NAMESPACE" -l "$label" --all-containers --tail=1000 > "$LOG_DIR/$TIMESTAMP/${COMPONENT_NAME}.log" 2>/dev/null || true
        print_status "Logs exported: $COMPONENT_NAME" "ok"
    done

    # Export service info
    kubectl get svc -n "$NAMESPACE" -o yaml > "$LOG_DIR/$TIMESTAMP/services.yaml" 2>/dev/null
    print_status "Services exported" "ok"

    # Export PVC info
    kubectl get pvc -n "$NAMESPACE" -o yaml > "$LOG_DIR/$TIMESTAMP/pvcs.yaml" 2>/dev/null
    print_status "PVCs exported" "ok"

    echo ""
    print_status "All logs exported to $LOG_DIR/$TIMESTAMP/" "ok"
}

show_quick_fixes() {
    print_header "Quick Fixes"

    echo ""
    echo "Common fixes for issues:"
    echo ""
    echo "1. Restart all Airflow components:"
    echo "   kubectl rollout restart deployment/airflow-webserver -n ldp"
    echo "   kubectl rollout restart deployment/airflow-scheduler -n ldp"
    echo ""
    echo "2. Restart Spark cluster:"
    echo "   kubectl rollout restart deployment/spark-master -n ldp"
    echo "   kubectl rollout restart deployment/spark-worker -n ldp"
    echo ""
    echo "3. Initialize MinIO buckets:"
    echo "   make init-minio"
    echo ""
    echo "4. Full platform restart:"
    echo "   make stop && make start"
    echo ""
    echo "5. Clean restart (warning: destroys all data):"
    echo "   make cleanup && make setup && make start && make init-minio"
    echo ""
}

show_urls() {
    print_header "Service URLs"

    MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "unknown")

    echo ""
    echo "Access services using port forwarding:"
    echo ""
    echo "  Airflow:    make airflow-forward  -> http://localhost:8080"
    echo "  MinIO:      make minio-forward    -> http://localhost:9001"
    echo "  Spark:      make spark-forward    -> http://localhost:8080"
    echo "  Jupyter:    make jupyter-forward  -> http://localhost:8888"
    echo "  Grafana:    kubectl port-forward -n ldp svc/grafana 3000:3000 -> http://localhost:3000"
    echo "  Prometheus: kubectl port-forward -n ldp svc/prometheus 9090:9090 -> http://localhost:9090"
    echo ""
    echo "Or access via NodePort (Minikube IP: $MINIKUBE_IP):"
    kubectl get svc -n ldp -o custom-columns="SERVICE:.metadata.name,TYPE:.spec.type,NODEPORT:.spec.ports[*].nodePort" | grep NodePort || echo "No NodePort services found"
    echo ""
}

run_quick_check() {
    check_prerequisites
    check_pods
    check_components
    show_urls
}

run_full_check() {
    check_prerequisites
    check_pods
    check_services
    check_pvcs
    check_resources
    check_events
    check_components
    check_connectivity
    show_urls
    show_quick_fixes
}

# Main
case "${1:-}" in
    --quick|-q)
        run_quick_check
        ;;
    --full|-f)
        run_full_check
        ;;
    --export-logs|-e)
        check_prerequisites
        export_logs
        ;;
    --help|-h)
        echo "LDP Troubleshooting Script"
        echo ""
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  --quick, -q       Quick health check (default)"
        echo "  --full, -f        Full diagnostic check"
        echo "  --export-logs, -e Export all logs to ./logs/"
        echo "  --help, -h        Show this help"
        echo ""
        ;;
    *)
        run_quick_check
        ;;
esac

echo ""
print_status "Troubleshooting complete" "ok"
echo ""
