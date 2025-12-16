#!/bin/bash
# Import Grafana dashboards for Local Data Platform
# Usage: ./monitoring/import-dashboards.sh

set -e

GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
GRAFANA_USER="${GRAFANA_USER:-admin}"
GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-admin}"
DASHBOARD_DIR="$(dirname "$0")/dashboards"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "LDP - Grafana Dashboard Import"
echo "=========================================="
echo ""
echo "Grafana URL: $GRAFANA_URL"
echo "Dashboard directory: $DASHBOARD_DIR"
echo ""

# Check if Grafana is accessible
echo "Checking Grafana connection..."
if ! curl -s -o /dev/null -w "%{http_code}" "$GRAFANA_URL/api/health" | grep -q "200"; then
    echo -e "${RED}Error: Cannot connect to Grafana at $GRAFANA_URL${NC}"
    echo ""
    echo "Make sure Grafana is running and port-forwarded:"
    echo "  make grafana-forward"
    echo ""
    echo "Or set GRAFANA_URL environment variable:"
    echo "  GRAFANA_URL=http://your-grafana:3000 ./monitoring/import-dashboards.sh"
    exit 1
fi
echo -e "${GREEN}Connected to Grafana${NC}"
echo ""

# Import each dashboard
import_dashboard() {
    local file=$1
    local name=$(basename "$file" .json)

    echo -n "Importing $name... "

    # Wrap dashboard in the required format for import
    local payload=$(jq '{dashboard: ., overwrite: true, folderId: 0}' "$file")

    local response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -u "$GRAFANA_USER:$GRAFANA_PASSWORD" \
        -d "$payload" \
        "$GRAFANA_URL/api/dashboards/db")

    if echo "$response" | grep -q '"status":"success"'; then
        echo -e "${GREEN}OK${NC}"
    elif echo "$response" | grep -q '"uid"'; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}FAILED${NC}"
        echo "  Response: $response"
    fi
}

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}Warning: jq not installed. Using simple import method.${NC}"
    echo ""

    for file in "$DASHBOARD_DIR"/*.json; do
        if [ -f "$file" ]; then
            name=$(basename "$file" .json)
            echo -n "Importing $name... "

            response=$(curl -s -X POST \
                -H "Content-Type: application/json" \
                -u "$GRAFANA_USER:$GRAFANA_PASSWORD" \
                -d "{\"dashboard\": $(cat "$file"), \"overwrite\": true}" \
                "$GRAFANA_URL/api/dashboards/db")

            if echo "$response" | grep -q '"uid"'; then
                echo -e "${GREEN}OK${NC}"
            else
                echo -e "${RED}FAILED${NC}"
            fi
        fi
    done
else
    # Import all dashboards
    for file in "$DASHBOARD_DIR"/*.json; do
        if [ -f "$file" ]; then
            import_dashboard "$file"
        fi
    done
fi

echo ""
echo "=========================================="
echo "Import complete!"
echo ""
echo "Access Grafana at: $GRAFANA_URL"
echo "Dashboards are available under 'Dashboards' menu"
echo "=========================================="
