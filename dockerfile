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

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
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

ENV DB_HOST=forensic-db
ENV DB_PORT=5432

# Copy startup script from scripts/ folder
COPY scripts/start-forensic-platform.sh .

# Make startup script executable
RUN chmod +x /app/start-forensic-platform.sh

# Expose ports for JupyterLab and Streamlit
EXPOSE 8888 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8888 && curl -f http://localhost:8501

# Set default command
CMD ["/app/start-forensic-platform.sh", "both"]

# Metadata labels
LABEL org.opencontainers.image.title="Mariupol Urbicide Forensic Analytics Platform"
LABEL org.opencontainers.image.description="Containerized forensic analysis platform for documenting administrative violence in occupied Mariupol"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Forensic Research Team"
LABEL forensic.project="mariupol_urbicide"
LABEL forensic.database="postgresql_postgis"
