#!/bin/bash

echo "Starting Psycho Monitoring System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Build and start containers
echo "Building and starting containers..."
docker-compose up -d --build

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 10

# Initialize database
echo "Initializing database..."
docker exec -i edupulse_db psql -U postgres -d edupulse_db -c "CREATE DATABASE IF NOT EXISTS edupulse_db;" 2>/dev/null

echo ""
echo "========================================"
echo "Application is starting!"
echo "========================================"
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "Keycloak: http://localhost:8080"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop: docker-compose down"

# Show logs
docker-compose logs -f
