# Voxify Project Makefile

.PHONY: help install lint format test test-quick build up down clean dev logs shell-backend shell-frontend

# Default target
help:
	@echo "Available targets:"
	@echo "  install - Install all dependencies"
	@echo "  lint    - Run linting for backend and frontend"
	@echo "  format  - Format code for backend and frontend"
	@echo "  test    - Run full test suite with Docker"
	@echo "  test-frontend - Run frontend tests"
	@echo "  build   - Build Docker images"
	@echo "  up      - Start services with docker-compose"
	@echo "  down    - Stop services"
	@echo "  test-quick - Run tests without full Docker rebuild"
	@echo "  logs    - Show logs from running services"
	@echo "  shell-backend  - Open shell in backend container"
	@echo "  shell-frontend - Open shell in frontend container"
	@echo "  clean   - Clean up Docker resources"
	@echo "  dev     - Install, lint, build, and start services"

# Install dependencies
install:
	@echo "Installing dependencies..."
	cd backend && pip install -r requirements.txt && pip install -r requirements-dev.txt
	cd frontend && npm ci
	@echo "✅ Dependencies installed"

# Linting
lint:
	@echo "Running linting..."
	cd backend && black --check . && flake8 .
	cd frontend && npm run lint && npm run format:check
	@echo "✅ Linting completed"

# Formatting
format:
	@echo "Formatting code..."
	cd backend && black .
	cd frontend && npm run format
	@echo "✅ Code formatted"

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose build
	@echo "✅ Images built"

# Full test suite (uses docker-compose)
test: build
	@echo "Running tests..."
	docker-compose run --rm tests
	@echo "✅ Tests completed"

# Quick test (reuses existing images)
test-quick:
	@echo "Running quick tests..."
	docker-compose run --rm tests
	@echo "✅ Quick tests completed"

# Frontend test suite
test-frontend:
	@echo "Running frontend tests..."
	docker-compose run --rm -e CI=true frontend npm run test:ci

# Docker Compose operations
up:
	docker-compose up -d
	@echo "✅ Services started"

down:
	docker-compose down
	@echo "✅ Services stopped"

# Show logs
logs:
	docker-compose logs -f

# Shell access for debugging
shell-backend:
	docker-compose run --rm api /bin/bash

shell-frontend:
	docker-compose run --rm frontend /bin/sh

# Cleanup
clean:
	docker system prune -f
	docker volume prune -f
	@echo "✅ Cleanup completed"

# Development workflow
dev: install lint build up
	@echo "✅ Development environment ready!"

# Build only the backend and db-init services
backend-build:
	@echo "Building backend services..."
	docker-compose build api db-init
	@echo "✅ Backend services built"

# Start only the backend and db-init services
backend-up:
	@echo "Starting backend services..."
	docker-compose up -d db-init api
	@echo "✅ Backend is running on port 8000"

# Stop only the backend services
backend-down:
	@echo "Stopping backend services..."
	docker-compose stop api db-init
	@echo "✅ Backend services stopped"

# View logs for the backend
backend-logs:
	docker-compose logs -f api db-init

# Shell into backend container
shell-api:
	docker-compose exec api /bin/bash

backend-prod:
	docker buildx build --platform linux/amd64 -t madelahn/voxify-api:latest ./backend