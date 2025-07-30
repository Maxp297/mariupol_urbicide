#!/bin/bash
# Forensic Toponymic Database Deployment Script
# Based on Opus research report recommendations
# Optimized for 8GB memory constraints

set -e

# Configuration
DB_NAME="mariupol_forensic"
DB_USER="forensic_user"
DB_PASSWORD="${DB_PASSWORD:-forensic_secure_2024}"
PROJECT_ROOT="${PROJECT_ROOT:-/Users/alexeykovalev/Desktop/urbicide_project}"

echo "=== Forensic Toponymic Database Deployment ==="
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Project Root: $PROJECT_ROOT"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "Error: PostgreSQL is not installed. Please install PostgreSQL first."
    echo "On macOS: brew install postgresql postgis"
    exit 1
fi

# Check if PostGIS is available
if ! psql -c "SELECT PostGIS_Version();" template1 2>/dev/null; then
    echo "Warning: PostGIS may not be properly installed."
    echo "On macOS: brew install postgis"
fi

# Start PostgreSQL service if not running
if ! pg_isready -q; then
    echo "Starting PostgreSQL service..."
    if command -v brew &> /dev/null; then
        brew services start postgresql
    else
        sudo systemctl start postgresql
    fi
    sleep 3
fi

# Create database and user
echo "Creating database and user..."
psql -c "CREATE DATABASE $DB_NAME;" postgres 2>/dev/null || echo "Database $DB_NAME already exists"
psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" postgres 2>/dev/null || echo "User $DB_USER already exists"
psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" postgres
psql -c "ALTER USER $DB_USER CREATEDB;" postgres

# Configure PostgreSQL for forensic workload (8GB memory optimization)
echo "Configuring PostgreSQL for forensic workload..."

# Find PostgreSQL config file
PG_CONFIG=$(psql -t -c "SHOW config_file;" $DB_NAME)
PG_CONFIG=$(echo $PG_CONFIG | xargs)  # Trim whitespace

if [ -f "$PG_CONFIG" ]; then
    echo "Found PostgreSQL config: $PG_CONFIG"
    
    # Backup original config
    sudo cp "$PG_CONFIG" "$PG_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Apply Opus-recommended settings for 8GB system
    sudo tee -a "$PG_CONFIG" > /dev/null << EOF

# Forensic Toponymic Database Optimization (Opus recommendations)
# Memory settings for 8GB system
shared_buffers = 2GB                    # 25% of RAM
effective_cache_size = 6GB              # 75% of RAM  
work_mem = 32MB                         # Conservative for multilingual text
maintenance_work_mem = 512MB            # For index creation
max_wal_size = 2GB                      # Larger WAL for bulk operations

# Connection settings
max_connections = 100                   # Reasonable for forensic workload
shared_preload_libraries = 'pg_stat_statements'

# Query optimization for fuzzy matching
random_page_cost = 1.1                 # Assume SSD storage
effective_io_concurrency = 200         # SSD optimization
default_statistics_target = 100        # Better query planning

# Logging for forensic audit trail
log_statement = 'mod'                  # Log all modifications
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0

# Forensic data integrity
fsync = on                             # Ensure data durability
synchronous_commit = on                # Wait for WAL write
full_page_writes = on                  # Protect against partial writes
wal_log_hints = on                     # Enable page checksums

EOF

    echo "PostgreSQL configuration updated. Restart required."
    
    # Restart PostgreSQL
    if command -v brew &> /dev/null; then
        brew services restart postgresql
    else
        sudo systemctl restart postgresql
    fi
    
    sleep 5
else
    echo "Warning: Could not locate PostgreSQL config file. Manual configuration may be needed."
fi

# Create database schema
echo "Creating forensic toponymic schema..."
psql -d $DB_NAME -f "$PROJECT_ROOT/scripts/create_toponymic_database.sql"

# Set environment variables
echo "Setting up environment variables..."
cat > "$PROJECT_ROOT/.env.forensic" << EOF
# Forensic Toponymic Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
PROJECT_ROOT=$PROJECT_ROOT

# Forensic settings
FORENSIC_CHAIN_CUSTODY=true
ENABLE_AUDIT_LOGGING=true
CONFIDENCE_THRESHOLD=0.7
EOF

echo "Environment configuration saved to .env.forensic"

# Install Python dependencies
echo "Installing Python dependencies..."
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment and install dependencies
source .venv/bin/activate

# Install required packages for forensic toponymic system
pip install --upgrade pip
pip install psycopg2-binary pandas rapidfuzz geojson shapely

# Add forensic-specific requirements
cat >> requirements.txt << EOF

# Forensic Toponymic Database Requirements
psycopg2-binary>=2.9.0
rapidfuzz>=3.0.0
geojson>=3.0.0
shapely>=2.0.0
EOF

pip install -r requirements.txt

echo "Python dependencies installed."

# Create logs directory
mkdir -p "$PROJECT_ROOT/logs"
chmod 755 "$PROJECT_ROOT/logs"

# Test database connection
echo "Testing database connection..."
python3 -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        host='localhost',
        port='5432', 
        database='$DB_NAME',
        user='$DB_USER',
        password='$DB_PASSWORD'
    )
    print('✓ Database connection successful')
    
    # Test PostGIS
    cur = conn.cursor()
    cur.execute('SELECT PostGIS_Version();')
    version = cur.fetchone()[0]
    print(f'✓ PostGIS version: {version}')
    
    # Test forensic schema
    cur.execute('SELECT COUNT(*) FROM forensic_toponymy.streets;')
    print('✓ Forensic schema accessible')
    
    conn.close()
    print('✓ All tests passed')
except Exception as e:
    print(f'✗ Database test failed: {e}')
    exit(1)
"

# Create quick-start script
cat > "$PROJECT_ROOT/start_forensic_system.sh" << 'EOF'
#!/bin/bash
# Quick-start script for forensic toponymic system

PROJECT_ROOT="${PROJECT_ROOT:-/Users/alexeykovalev/Desktop/urbicide_project}"
cd "$PROJECT_ROOT"

# Load environment
if [ -f ".env.forensic" ]; then
    export $(cat .env.forensic | grep -v '^#' | xargs)
fi

# Activate virtual environment
source .venv/bin/activate

echo "=== Forensic Toponymic System Ready ==="
echo "Database: $DB_NAME"
echo "Project Root: $PROJECT_ROOT"
echo ""
echo "Available scripts:"
echo "  python scripts/populate_toponymic_database.py    # Populate with existing data"
echo "  python scripts/generate_comprehensive_variants.py # Generate address variants"
echo "  python scripts/forensic_fuzzy_matcher.py         # Test fuzzy matching"
echo ""
echo "Database connection test:"
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(host='$DB_HOST', port='$DB_PORT', database='$DB_NAME', user='$DB_USER', password='$DB_PASSWORD')
    print('✓ Connected to forensic database')
    conn.close()
except Exception as e:
    print(f'✗ Connection failed: {e}')
"
EOF

chmod +x "$PROJECT_ROOT/start_forensic_system.sh"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "✓ PostgreSQL database '$DB_NAME' created"
echo "✓ Forensic toponymic schema installed"
echo "✓ Python environment configured"
echo "✓ Configuration files created"
echo ""
echo "Next steps:"
echo "1. Source environment: source .env.forensic"
echo "2. Start system: ./start_forensic_system.sh"
echo "3. Populate database: python scripts/populate_toponymic_database.py"
echo "4. Generate variants: python scripts/generate_comprehensive_variants.py"
echo ""
echo "Database connection details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Schema: forensic_toponymy"
echo ""
echo "For manual connection: psql -h localhost -U $DB_USER -d $DB_NAME"
