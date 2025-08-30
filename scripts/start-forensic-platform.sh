#!/bin/bash
set -e

echo "*** Starting Mariupol Forensic Analytics Platform ***"
echo "===================================================="

# Wait for PostgreSQL database to be ready
echo "[INFO] Waiting for PostgreSQL database..."
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "Waiting for database connection..."
  sleep 5
done

echo "[SUCCESS] Database connection established"

# Check if database schema exists, if not deploy it
echo "[INFO] Checking database schema..."
if ! psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\dt forensic_toponymy.*" > /dev/null 2>&1; then
    echo "[INFO] Deploying forensic database schema..."
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f /app/scripts/create_toponymic_database.sql
    echo "[SUCCESS] Schema deployed"
else
    echo "[SUCCESS] Schema already exists"
fi

# Check if database is populated, if not populate it
echo "[INFO] Checking database population..."
if ! psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM forensic_toponymy.evidence_sources;" > /dev/null 2>&1; then
    echo "[INFO] Populating forensic database..."
    cd /app && python scripts/populate_toponymic_database.py
    echo "[SUCCESS] Database populated"
else
    echo "[SUCCESS] Database already populated"
fi

# Start services based on command
case "${1:-jupyter}" in
    "jupyter")
        echo "[INFO] Starting JupyterLab on port 8888..."
        echo "[INFO] Access at: http://localhost:8888"
        echo "[INFO] Token: $FORENSIC_TOKEN"
        jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root \
          --NotebookApp.token="$FORENSIC_TOKEN" \
          --NotebookApp.password="" \
          --NotebookApp.notebook_dir="/app"
        ;;
    "streamlit")
        echo "[INFO] Starting Streamlit Dashboard on port 8501..."
        echo "[INFO] Access at: http://localhost:8501"
        streamlit run scripts/forensic_dashboard.py \
          --server.address=0.0.0.0 \
          --server.port=8501 \
          --server.headless=true \
          --server.fileWatcherType=none
        ;;
    "both")
        echo "[INFO] Starting both JupyterLab and Streamlit..."
        # Start JupyterLab in background
        jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root \
          --NotebookApp.token="$FORENSIC_TOKEN" \
          --NotebookApp.password="" \
          --NotebookApp.notebook_dir="/app" &
        # Start Streamlit in foreground
        streamlit run scripts/forensic_dashboard.py \
          --server.address=0.0.0.0 \
          --server.port=8501 \
          --server.headless=true \
          --server.fileWatcherType=none
        ;;
    *)
        echo "Usage: $0 {jupyter|streamlit|both}"
        echo "Starting JupyterLab by default..."
        exec "$0" jupyter
        ;;
esac
