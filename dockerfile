# Mariupol Urbicide Forensic Analytics Platform
# Python analytics container for forensic analysis

FROM python:3.11-slim

# Install system dependencies for geospatial and forensic analysis
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    libspatialindex-dev \
    git \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional forensic analysis packages
RUN pip install --no-cache-dir \
    jupyter \
    jupyterlab \
    plotly \
    dash \
    streamlit \
    seaborn \
    networkx \
    scikit-learn \
    nltk \
    spacy \
    textblob \
    wordcloud \
    folium \
    streamlit-folium \
    geoplot \
    contextily

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/analysis /app/output /app/notebooks /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PROJECT_ROOT=/app
ENV POSTGRES_HOST=forensic-db
ENV POSTGRES_DB=mariupol_forensic_toponyms
ENV POSTGRES_USER=forensic
ENV POSTGRES_PASSWORD=forensic_secure_2024

# Create startup script for analytics services
RUN echo '#!/bin/bash' > /app/start-forensic-platform.sh && \
    echo 'set -e' >> /app/start-forensic-platform.sh && \
    echo '' >> /app/start-forensic-platform.sh && \
    echo 'echo "*** Starting Mariupol Forensic Analytics Platform ***"' >> /app/start-forensic-platform.sh && \
    echo 'echo "===================================================="' >> /app/start-forensic-platform.sh && \
    echo '' >> /app/start-forensic-platform.sh && \
    echo '# Wait for PostgreSQL database to be ready' >> /app/start-forensic-platform.sh && \
    echo 'echo "[INFO] Waiting for PostgreSQL database..."' >> /app/start-forensic-platform.sh && \
    echo 'until pg_isready -h $POSTGRES_HOST -p 5432 -U $POSTGRES_USER; do' >> /app/start-forensic-platform.sh && \
    echo '  echo "Waiting for database connection..."' >> /app/start-forensic-platform.sh && \
    echo '  sleep 5' >> /app/start-forensic-platform.sh && \
    echo 'done' >> /app/start-forensic-platform.sh && \
    echo '' >> /app/start-forensic-platform.sh && \
    echo 'echo "[SUCCESS] Database connection established"' >> /app/start-forensic-platform.sh && \
    echo '' >> /app/start-forensic-platform.sh && \
    echo '# Check if database schema exists, if not deploy it' >> /app/start-forensic-platform.sh && \
    echo 'echo "[INFO] Checking database schema..."' >> /app/start-forensic-platform.sh && \
    echo 'if ! psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "\\dt forensic_toponymy.*" > /dev/null 2>&1; then' >> /app/start-forensic-platform.sh && \
    echo '    echo "[INFO] Deploying forensic database schema..."' >> /app/start-forensic-platform.sh && \
    echo '    PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -f /app/scripts/create_toponymic_database.sql' >> /app/start-forensic-platform.sh && \
    echo '    echo "[SUCCESS] Schema deployed"' >> /app/start-forensic-platform.sh && \
    echo 'else' >> /app/start-forensic-platform.sh && \
    echo '    echo "[SUCCESS] Schema already exists"' >> /app/start-forensic-platform.sh && \
    echo 'fi' >> /app/start-forensic-platform.sh && \
    echo '' >> /app/start-forensic-platform.sh && \
    echo '# Check if database is populated, if not populate it' >> /app/start-forensic-platform.sh && \
    echo 'echo "[INFO] Checking database population..."' >> /app/start-forensic-platform.sh && \
    echo 'if ! psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT COUNT(*) FROM forensic_toponymy.evidence_sources;" > /dev/null 2>&1; then' >> /app/start-forensic-platform.sh && \
    echo '    echo "[INFO] Populating forensic database..."' >> /app/start-forensic-platform.sh && \
    echo '    cd /app && python scripts/populate_toponymic_database.py' >> /app/start-forensic-platform.sh && \
    echo '    echo "[SUCCESS] Database populated"' >> /app/start-forensic-platform.sh && \
    echo 'else' >> /app/start-forensic-platform.sh && \
    echo '    echo "[SUCCESS] Database already populated"' >> /app/start-forensic-platform.sh && \
    echo 'fi' >> /app/start-forensic-platform.sh && \
    echo '' >> /app/start-forensic-platform.sh && \
    echo '# Start services based on command' >> /app/start-forensic-platform.sh && \
    echo 'case "${1:-jupyter}" in' >> /app/start-forensic-platform.sh && \
    echo '    "jupyter")' >> /app/start-forensic-platform.sh && \
    echo '        echo "[INFO] Starting JupyterLab on port 8888..."' >> /app/start-forensic-platform.sh && \
    echo '        echo "[INFO] Access at: http://localhost:8888"' >> /app/start-forensic-platform.sh && \
    echo '        echo "[INFO] Token: forensic_analysis_2024"' >> /app/start-forensic-platform.sh && \
    echo '        ' >> /app/start-forensic-platform.sh && \
    echo '        jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root \' >> /app/start-forensic-platform.sh && \
    echo '          --NotebookApp.token="forensic_analysis_2024" \' >> /app/start-forensic-platform.sh && \
    echo '          --NotebookApp.password="" \' >> /app/start-forensic-platform.sh && \
    echo '          --NotebookApp.notebook_dir="/app"' >> /app/start-forensic-platform.sh && \
    echo '        ;;' >> /app/start-forensic-platform.sh && \
    echo '    "streamlit")' >> /app/start-forensic-platform.sh && \
    echo '        echo "[INFO] Starting Streamlit Dashboard on port 8501..."' >> /app/start-forensic-platform.sh && \
    echo '        echo "[INFO] Access at: http://localhost:8501"' >> /app/start-forensic-platform.sh && \
    echo '        ' >> /app/start-forensic-platform.sh && \
    echo '        streamlit run scripts/forensic_dashboard.py \' >> /app/start-forensic-platform.sh && \
    echo '          --server.address=0.0.0.0 \' >> /app/start-forensic-platform.sh && \
    echo '          --server.port=8501 \' >> /app/start-forensic-platform.sh && \
    echo '          --server.headless=true \' >> /app/start-forensic-platform.sh && \
    echo '          --server.fileWatcherType=none' >> /app/start-forensic-platform.sh && \
    echo '        ;;' >> /app/start-forensic-platform.sh && \
    echo '    "both")' >> /app/start-forensic-platform.sh && \
    echo '        echo "[INFO] Starting both JupyterLab and Streamlit..."' >> /app/start-forensic-platform.sh && \
    echo '        ' >> /app/start-forensic-platform.sh && \
    echo '        # Start JupyterLab in background' >> /app/start-forensic-platform.sh && \
    echo '        jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root \' >> /app/start-forensic-platform.sh && \
    echo '          --NotebookApp.token="forensic_analysis_2024" \' >> /app/start-forensic-platform.sh && \
    echo '          --NotebookApp.password="" \' >> /app/start-forensic-platform.sh && \
    echo '          --NotebookApp.notebook_dir="/app" &' >> /app/start-forensic-platform.sh && \
    echo '        ' >> /app/start-forensic-platform.sh && \
    echo '        # Start Streamlit in foreground' >> /app/start-forensic-platform.sh && \
    echo '        streamlit run scripts/forensic_dashboard.py \' >> /app/start-forensic-platform.sh && \
    echo '          --server.address=0.0.0.0 \' >> /app/start-forensic-platform.sh && \
    echo '          --server.port=8501 \' >> /app/start-forensic-platform.sh && \
    echo '          --server.headless=true \' >> /app/start-forensic-platform.sh && \
    echo '          --server.fileWatcherType=none' >> /app/start-forensic-platform.sh && \
    echo '        ;;' >> /app/start-forensic-platform.sh && \
    echo '    *)' >> /app/start-forensic-platform.sh && \
    echo '        echo "Usage: $0 {jupyter|streamlit|both}"' >> /app/start-forensic-platform.sh && \
    echo '        echo "Starting JupyterLab by default..."' >> /app/start-forensic-platform.sh && \
    echo '        exec "$0" jupyter' >> /app/start-forensic-platform.sh && \
    echo '        ;;' >> /app/start-forensic-platform.sh && \
    echo 'esac' >> /app/start-forensic-platform.sh

# Make startup script executable
RUN chmod +x /app/start-forensic-platform.sh

# Expose ports for JupyterLab and Streamlit
EXPOSE 8888 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8888 || curl -f http://localhost:8501 || exit 1

# Set default command
CMD ["/app/start-forensic-platform.sh", "both"]

# Metadata labels
LABEL org.opencontainers.image.title="Mariupol Urbicide Forensic Analytics Platform"
LABEL org.opencontainers.image.description="Containerized forensic analysis platform for documenting administrative violence in occupied Mariupol"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Forensic Research Team"
LABEL forensic.project="mariupol_urbicide"
LABEL forensic.database="postgresql_postgis"