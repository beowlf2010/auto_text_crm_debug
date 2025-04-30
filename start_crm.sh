#!/bin/bash

echo "🔄 Stopping and removing existing containers..."
docker-compose down --volumes --remove-orphans

echo "🧹 Removing dangling images..."
docker image prune -f

echo "🚀 Building and starting all services..."
docker-compose up --build
