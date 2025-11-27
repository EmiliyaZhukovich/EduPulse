# PowerShell script to start the application

Write-Host "Starting Psycho Monitoring System..." -ForegroundColor Green

# Check if Docker is running
$dockerCheck = docker info 2>$null
if (-not $dockerCheck) {
    Write-Host "Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Stop existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose down

# Build and start containers
Write-Host "Building and starting containers..." -ForegroundColor Yellow
docker-compose up -d --build

# Wait for database to be ready
Write-Host "Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Yellow
docker exec -i edupulse_db psql -U postgres -d edupulse_db -c "CREATE DATABASE IF NOT EXISTS edupulse_db;" 2>$null

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Application is starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Keycloak: http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "View logs: docker-compose logs -f" -ForegroundColor Yellow
Write-Host "Stop: docker-compose down" -ForegroundColor Yellow

# Show logs
docker-compose logs -f
