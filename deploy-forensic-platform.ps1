# Mariupol Urbicide Forensic Analytics Platform Deployment Script (PowerShell)
# Builds and deploys the complete containerized forensic system
# Run as administrator

param(
    [string]$Command = "deploy"
)

function Write-Info($msg)    { Write-Host "[INFO] $msg" -ForegroundColor Blue }
function Write-Success($msg) { Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Warning($msg) { Write-Host "[WARNING] $msg" -ForegroundColor Yellow }
function Write-ErrorMsg($msg){ Write-Host "[ERROR] $msg" -ForegroundColor Red }

# Check for Administrator privileges
function Check-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-ErrorMsg "This script must be run as Administrator. Please right-click PowerShell and select 'Run as administrator'."
        exit 1
    }
}

# Check PowerShell script execution policy
function Check-ExecutionPolicy {
    $policy = Get-ExecutionPolicy
    if ($policy -eq "Restricted" -or $policy -eq "Undefined") {
        Write-ErrorMsg "PowerShell script execution is disabled on this system."
        Write-Host "To enable script execution, run the following command in an Administrator PowerShell window:"
        Write-Host "  Set-ExecutionPolicy RemoteSigned"
        Write-Host "Or, for all users:"
        Write-Host "  Set-ExecutionPolicy RemoteSigned -Scope LocalMachine"
        exit 1
    }
}

function Check-Prerequisites {
    Write-Info "Checking prerequisites..."

    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-ErrorMsg "Docker is not installed. Please install Docker Desktop first."
        exit 1
    }
    if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Write-ErrorMsg "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    }
    try {
        docker info | Out-Null
    } catch {
        Write-ErrorMsg "Docker daemon is not running. Please start Docker Desktop first."
        exit 1
    }
    Write-Success "Prerequisites check passed"
}

function Create-Directories {
    Write-Info "Creating necessary directories..."
    if (-not (Test-Path "analysis")) { New-Item -ItemType Directory -Path "analysis" | Out-Null }
    if (-not (Test-Path "output"))   { New-Item -ItemType Directory -Path "output"   | Out-Null }
    Write-Success "Directories created"
}

function Update-Requirements {
    Write-Info "Updating requirements.txt with forensic analysis packages..."
    $reqFile = "requirements.txt"
    if (-not (Select-String -Path $reqFile -Pattern "streamlit" -Quiet)) {
        Add-Content $reqFile @"
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
"@
    }
    Write-Success "Requirements updated"
}

function Build-Images {
    Write-Info "Building Docker images..."
    docker build -t mariupol-forensic-platform:latest . 
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Failed to build Docker image"
        exit 1
    }
    Write-Success "Docker images built successfully"
}

function Deploy-Platform {
    Write-Info "Deploying forensic analytics platform..."
    docker-compose down --remove-orphans 2>$null
    docker-compose up -d forensic-db forensic-analytics
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Failed to deploy platform. Check Docker logs for details."
        exit 1
    }
    Write-Success "Platform deployment initiated"
}

function Wait-For-Services {
    Write-Info "Waiting for services to be ready..."

    Write-Info "Waiting for PostgreSQL database..."
    $dbReady = $false
    for ($i=1; $i -le 30; $i++) {
        try {
            docker exec mariupol-forensic-db pg_isready -U forensic -d mariupol_forensic_toponyms | Out-Null
            $dbReady = $true
            Write-Success "Database is ready"
            break
        } catch {}
        Start-Sleep -Seconds 10
    }
    if (-not $dbReady) {
        Write-ErrorMsg "Database failed to start within 5 minutes"
        exit 1
    }

    Write-Info "Waiting for JupyterLab..."
    $jlReady = $false
    for ($i=1; $i -le 20; $i++) {
        try {
            Invoke-WebRequest -Uri "http://localhost:8888" -UseBasicParsing | Out-Null
            $jlReady = $true
            Write-Success "JupyterLab is ready"
            break
        } catch {}
        Start-Sleep -Seconds 15
    }
    if (-not $jlReady) { Write-Warning "JupyterLab may still be starting up" }

    Write-Info "Waiting for Streamlit dashboard..."
    $stReady = $false
    for ($i=1; $i -le 20; $i++) {
        try {
            Invoke-WebRequest -Uri "http://localhost:8501" -UseBasicParsing | Out-Null
            $stReady = $true
            Write-Success "Streamlit dashboard is ready"
            break
        } catch {}
        Start-Sleep -Seconds 15
    }
    if (-not $stReady) { Write-Warning "Streamlit dashboard may still be starting up" }
}

function Show-Access-Info {
    Write-Host ""
    Write-Host " Forensic Analytics Platform Deployed Successfully!"
    Write-Host "===================================================="
    Write-Host ""
    Write-Host " Access Points:"
    Write-Host "   JupyterLab:        http://localhost:8888"
    Write-Host "     Token:             forensic_analysis_2024"
    Write-Host ""
    Write-Host "   Streamlit Dashboard: http://localhost:8501"
    Write-Host "     Interactive forensic analytics interface"
    Write-Host ""
    Write-Host "   PostgreSQL Database: localhost:5432"
    Write-Host "     Database:           mariupol_forensic_toponyms"
    Write-Host "     Username:           forensic"
    Write-Host "     Password:           forensic_secure_2024"
    Write-Host ""
    Write-Host " Management Commands:"
    Write-Host "   View logs:            docker-compose logs -f"
    Write-Host "   Stop platform:        docker-compose down"
    Write-Host "   Restart platform:     docker-compose restart"
    Write-Host "   Update platform:      ./deploy-forensic-platform.ps1"
    Write-Host ""
    Write-Host " Container Status:"
    docker-compose ps
    Write-Host ""
    Write-Host " Data Persistence:"
    Write-Host "   Database data:        ./docker-data/postgres/"
    Write-Host "   Jupyter notebooks:    ./docker-data/notebooks/"
    Write-Host "   Analysis logs:        ./docker-data/logs/"
    Write-Host "   Analysis output:      ./output/"
    Write-Host ""
    Write-Host "  Legal Notice:"
    Write-Host "This platform contains forensic evidence with maintained chain-of-custody."
    Write-Host "All data access and modifications are logged for legal proceedings."
    Write-Host ""
}

function Health-Check {
    Write-Info "Performing health check..."
    try {
        docker exec mariupol-forensic-db pg_isready -U forensic -d mariupol_forensic_toponyms | Out-Null
        Write-Success " Database: Healthy"
    } catch {
        Write-ErrorMsg " Database: Unhealthy"
    }
    try {
        Invoke-WebRequest -Uri "http://localhost:8888" -UseBasicParsing | Out-Null
        Write-Success " JupyterLab: Healthy"
    } catch {
        Write-Warning " JupyterLab: Not responding"
    }
    try {
        Invoke-WebRequest -Uri "http://localhost:8501" -UseBasicParsing | Out-Null
        Write-Success " Streamlit: Healthy"
    } catch {
        Write-Warning " Streamlit: Not responding"
    }
    $drive = Get-PSDrive -Name (Get-Location).Path.Substring(0,1)
    if ($drive.Free -gt 1GB) {
        Write-Success " Disk Space: Sufficient"
    } else {
        Write-Warning " Disk Space: Low (less than 1GB available)"
    }
}

function main($Command) {
    # Check permissions and execution policy
    Check-Admin
    Check-ExecutionPolicy

    switch ($Command) {
        "deploy" {
            Check-Prerequisites
            Create-Directories
            Update-Requirements
            Build-Images
            Deploy-Platform
            Wait-For-Services
            Show-Access-Info
        }
        "health" {
            Health-Check
        }
        "stop" {
            Write-Info "Stopping forensic platform..."
            docker-compose down
            Write-Success "Platform stopped"
        }
        "restart" {
            Write-Info "Restarting forensic platform..."
            docker-compose restart forensic-db forensic-analytics
            Write-Success "Platform restarted"
        }
        "logs" {
            docker-compose logs -f forensic-db forensic-analytics
        }
        "update" {
            Write-Info "Updating forensic platform..."
            docker-compose down
            docker-compose pull
            Build-Images
            Deploy-Platform
            Wait-For-Services
            Write-Success "Platform updated"
        }
        "dashboard-only" {
            Write-Info "Starting dashboard-only mode..."
            docker-compose --profile dashboard-only up -d forensic-db forensic-dashboard
            Wait-For-Services
            Write-Success "Dashboard-only mode started on port 8502"
        }
        "clean" {
            Write-Warning "This will remove all containers and images. Data will be preserved."
            $confirm = Read-Host "Are you sure? (y/N)"
            if ($confirm -eq "y" -or $confirm -eq "Y") {
                docker-compose down --rmi all --remove-orphans
                docker system prune -f
                Write-Success "Platform cleaned"
            }
        }
        default {
            Write-Host "Usage: .\deploy-forensic-platform.ps1 -Command {deploy|health|stop|restart|logs|update|dashboard-only|clean}"
            Write-Host ""
            Write-Host "Commands:"
            Write-Host "  deploy         - Deploy the complete forensic platform (default)"
            Write-Host "  health         - Check platform health status"
            Write-Host "  stop           - Stop all platform services"
            Write-Host "  restart        - Restart all platform services"
            Write-Host "  logs           - View platform logs (real-time)"
            Write-Host "  update         - Update and redeploy platform"
            Write-Host "  dashboard-only - Start only database and dashboard (port 8502)"
            Write-Host "  clean          - Remove all containers and images (keeps data)"
            exit 1
        }
    }
}

main $Command
