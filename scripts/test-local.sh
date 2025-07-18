#!/bin/bash
set -e

echo "Building base image..."
docker build -f backend/Dockerfile.base -t backend-base:latest backend

echo "Building services..."
docker compose build

echo "Initializing database..."
docker compose run --rm db-init

echo "Starting API..."
docker compose up -d api

echo "Waiting for API to start..."
sleep 20

echo "Running tests..."
docker compose run --rm tests

echo "Cleaning up..."
docker compose down --volumes

echo "Tests completed!"