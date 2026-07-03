#!/bin/bash
# deploy.sh
# Deployment script for the Claudable Backend on a VPS.

set -e

echo "Starting deployment of Claudable Backend..."

# 1. Update the code
echo "Pulling latest changes from git..."
git pull origin main

# 2. Rebuild and restart the backend using docker-compose
echo "Rebuilding and restarting Docker containers..."
cd backend
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

echo "Deployment completed successfully!"
echo "You can view logs by running: cd backend && docker-compose -f docker-compose.prod.yml logs -f"
