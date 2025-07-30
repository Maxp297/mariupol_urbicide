#!/bin/bash
set -e

# Mariupol Urbicide Forensic Analytics Platform Deployment Script
# Builds and deploys the complete containerized forensic system

echo " Mariupol Urbicide Forensic Analytics Platform"
echo "================================================"
echo "  Docker-powered forensic analysis system"
echo "  PostgreSQL + PostGIS + Python + Streamlit + JupyterLab"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    # Ensure output and analysis directories exist
    mkdir -p analysis
    mkdir -p output
    
    print_success "Directories created"
}

# Update requirements.txt with additional packages
update_requirements() {
    print_status "Updating requirements.txt with forensic analysis packages..."
    
    # Add Streamlit and visualization packages if not present
    if ! grep -q "streamlit" requirements.txt; then
        cat >> requirements.txt << EOF

# Forensic Analytics Dashboard
streamlit>=1.28.0
plotly>=5.17.0
folium>=0.14.0
streamlit-folium>=0.15.0
networkx>=3.2.1
seaborn>=0.12.2
wordcloud>=1.9.2
geoplot>=0.5.1
contextily>=1.4.0
EOF
    fi
    
    print_success "Requirements updated"
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build the forensic platform image
    docker build -t mariupol-forensic-platform:latest . || {
        print_error "Failed to build Docker image"
        exit 1
    }
    
    print_success "Docker images built successfully"
}

# Deploy the platform
deploy_platform() {
    print_status "Deploying forensic analytics platform..."
    
    # Stop any existing containers
    docker-compose down --remove-orphans 2>/dev/null || true
    
    # Start the platform
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d forensic-db forensic-analytics
    else
        docker compose up -d forensic-db forensic-analytics
    fi
    
    print_success "Platform deployment initiated"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for PostgreSQL database..."
    for i in {1..30}; do
        if docker exec mariupol-forensic-db pg_isready -U forensic -d mariupol_forensic_toponyms &>/dev/null; then
            print_success "Database is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Database failed to start within 5 minutes"
            exit 1
        fi
        sleep 10
    done
    
    # Wait for analytics platform (JupyterLab)
    print_status "Waiting for JupyterLab..."
    for i in {1..20}; do
        if curl -f http://localhost:8888 &>/dev/null; then
            print_success "JupyterLab is ready"
            break
        fi
        if [ $i -eq 20 ]; then
            print_warning "JupyterLab may still be starting up"
        fi
        sleep 15
    done
    
    # Wait for dashboard
    print_status "Waiting for Streamlit dashboard..."
    for i in {1..20}; do
        if curl -f http://localhost:8501 &>/dev/null; then
            print_success "Streamlit dashboard is ready"
            break
        fi
        if [ $i -eq 20 ]; then
            print_warning "Streamlit dashboard may still be starting up"
        fi
        sleep 15
    done
}

# Display access information
show_access_info() {
    echo ""
    echo " Forensic Analytics Platform Deployed Successfully!"
    echo "===================================================="
    echo ""
    echo " Access Points:"
    echo "   JupyterLab:        http://localhost:8888"
    echo "     Token:             forensic_analysis_2024"
    echo ""
    echo "   Streamlit Dashboard: http://localhost:8501"
    echo "     Interactive forensic analytics interface"
    echo ""
    echo "   PostgreSQL Database: localhost:5432"
    echo "     Database:           mariupol_forensic_toponyms"
    echo "     Username:           forensic"
    echo "     Password:           forensic_secure_2024"
    echo ""
    echo " Management Commands:"
    echo "   View logs:            docker-compose logs -f"
    echo "   Stop platform:        docker-compose down"
    echo "   Restart platform:     docker-compose restart"
    echo "   Update platform:      ./deploy-forensic-platform.sh"
    echo ""
    echo " Container Status:"
    docker-compose ps
    echo ""
    echo " Data Persistence:"
    echo "   Database data:        ./docker-data/postgres/"
    echo "   Jupyter notebooks:    ./docker-data/notebooks/"
    echo "   Analysis logs:        ./docker-data/logs/"
    echo "   Analysis output:      ./output/"
    echo ""
    echo "  Legal Notice:"
    echo "This platform contains forensic evidence with maintained chain-of-custody."
    echo "All data access and modifications are logged for legal proceedings."
    echo ""
}

# Health check
health_check() {
    print_status "Performing health check..."
    
    # Check database
    if docker exec mariupol-forensic-db pg_isready -U forensic -d mariupol_forensic_toponyms &>/dev/null; then
        print_success " Database: Healthy"
    else
        print_error " Database: Unhealthy"
    fi
    
    # Check JupyterLab
    if curl -f http://localhost:8888 &>/dev/null; then
        print_success " JupyterLab: Healthy"
    else
        print_warning " JupyterLab: Not responding"
    fi
    
    # Check Streamlit
    if curl -f http://localhost:8501 &>/dev/null; then
        print_success " Streamlit: Healthy"
    else
        print_warning " Streamlit: Not responding"
    fi
    
    # Check disk space
    available_space=$(df . | tail -1 | awk '{print $4}')
    if [ "$available_space" -gt 1000000 ]; then  # 1GB in KB
        print_success " Disk Space: Sufficient"
    else
        print_warning " Disk Space: Low (less than 1GB available)"
    fi
}

# Main deployment function
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            create_directories
            update_requirements
            build_images
            deploy_platform
            wait_for_services
            show_access_info
            ;;
        "health")
            health_check
            ;;
        "stop")
            print_status "Stopping forensic platform..."
            docker-compose down
            print_success "Platform stopped"
            ;;
        "restart")
            print_status "Restarting forensic platform..."
            docker-compose restart forensic-db forensic-analytics
            print_success "Platform restarted"
            ;;
        "logs")
            docker-compose logs -f forensic-db forensic-analytics
            ;;
        "update")
            print_status "Updating forensic platform..."
            docker-compose down
            docker-compose pull
            build_images
            deploy_platform
            wait_for_services
            print_success "Platform updated"
            ;;
        "dashboard-only")
            print_status "Starting dashboard-only mode..."
            docker-compose --profile dashboard-only up -d forensic-db forensic-dashboard
            wait_for_services
            print_success "Dashboard-only mode started on port 8502"
            ;;
        "clean")
            print_warning "This will remove all containers and images. Data will be preserved."
            read -p "Are you sure? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                docker-compose down --rmi all --remove-orphans
                docker system prune -f
                print_success "Platform cleaned"
            fi
            ;;
        *)
            echo "Usage: $0 {deploy|health|stop|restart|logs|update|dashboard-only|clean}"
            echo ""
            echo "Commands:"
            echo "  deploy        - Deploy the complete forensic platform (default)"
            echo "  health        - Check platform health status"
            echo "  stop          - Stop all platform services"
            echo "  restart       - Restart all platform services"
            echo "  logs          - View platform logs (real-time)"
            echo "  update        - Update and redeploy platform"
            echo "  dashboard-only - Start only database and dashboard (port 8502)"
            echo "  clean         - Remove all containers and images (keeps data)"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
