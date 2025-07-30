# Voxify Project Makefile

.PHONY: help install lint format test test-quick build up down clean dev logs shell-backend shell-frontend

# Default target
help:
	@echo "Available targets:"
	@echo " install       - Install all dependencies"
	@echo " lint          - Run linting for backend and frontend"
	@echo " format        - Format code for backend and frontend"
	@echo " test          - Run full test suite with Docker"
	@echo " test-frontend - Run frontend tests"
	@echo " build         - Build Docker images"
	@echo " up            - Start services with docker-compose"
	@echo " down          - Stop services"
	@echo " test-quick    - Run tests without full Docker rebuild"
	@echo " logs          - Show logs from running services"
	@echo " shell-backend - Open shell in backend container"
	@echo " shell-frontend- Open shell in frontend container"
	@echo " clean         - Clean up Docker resources"
	@echo " dev           - Install, lint, build, and start services"
	@echo " backend-up    - Start only backend services"
	@echo " backend-https - Start backend with HTTPS support"
	@echo " setup-certs   - Copy SSL certificates for Docker use"
	@echo " clean         - Clean up Docker resources"

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

# Setup SSL certificates for Docker
setup-certs:
	@echo "Setting up SSL certificates for Docker..."
	mkdir -p ./backend/certs
	sudo cp /etc/letsencrypt/live/milaniez-cheetah.duckdns.org/fullchain.pem ./backend/certs/
	sudo cp /etc/letsencrypt/live/milaniez-cheetah.duckdns.org/privkey.pem ./backend/certs/
	sudo chown $(USER):$(USER) ./backend/certs/*
	chmod 644 ./backend/certs/fullchain.pem
	chmod 600 ./backend/certs/privkey.pem
	@echo "✅ Certificates copied and permissions set"
 
 backend-up: setup-certs
	@echo "Starting backend services with HTTPS..."
	docker-compose up -d db-init
	SSL_CERT_FILE=/app/certs/fullchain.pem SSL_KEY_FILE=/app/certs/privkey.pem docker-compose run --rm -d -p 8000:8000 -v $(PWD)/backend/certs:/app/certs:ro api python startup.py --https
	@echo "✅ Backend is running with HTTPS on port 8000"