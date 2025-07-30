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
	sudo cp /etc/letsencrypt/live/milaniez-montagy.duckdns.org/fullchain.pem ./backend/certs/
	sudo cp /etc/letsencrypt/live/milaniez-montagy.duckdns.org/privkey.pem ./backend/certs/
	sudo chown $(USER):$(USER) ./backend/certs/*
	chmod 644 ./backend/certs/fullchain.pem
	chmod 600 ./backend/certs/privkey.pem
	@echo "✅ Certificates copied and permissions set"
 
# Production deployment targets
setup-nginx:
	@echo "Setting up nginx configuration..."
	sudo cp nginx/voxify.conf /etc/nginx/sites-available/voxify
	sudo ln -sf /etc/nginx/sites-available/voxify /etc/nginx/sites-enabled/
	sudo rm -f /etc/nginx/sites-enabled/default
	sudo nginx -t
	sudo systemctl restart nginx
	sudo systemctl enable nginx
	@echo "✅ Nginx configured and running"

# Production backend with nginx handling SSL
backend-prod: 
	@echo "Starting backend for production."
	docker-compose up -d db-init api
	@echo "✅ Backend running in production mode on port 8000"

# Full production setup
prod-deploy: setup-nginx backend-prod
	@echo "✅ Production deployment complete!"
	@echo "Your API is now available at: https://milaniez-montagy.duckdns.org"

# Check production status
prod-status:
	@echo "=== Nginx Status ==="
	sudo systemctl status nginx --no-pager -l
	@echo ""
	@echo "=== Backend Status ==="
	docker-compose ps
	@echo ""
	@echo "=== SSL Certificate Status ==="
	sudo certbot certificates
