# Voxify Project Makefile
.PHONY: help install lint reformat test test-backend test-frontend test-security test-quick build build-backend build-frontend \
        up up-backend up-full down clean dev logs shell db-build frontend setup-certs setup-nginx \
        prod-build prod-up prod-down prod-deploy prod-status prod-logs

# Default target
help:
	@echo "Available targets:"
	@echo " install         - Install all dependencies"
	@echo " lint            - Run linting for backend and frontend"
	@echo " reformat        - Format code for backend and frontend"
	@echo ""
	@echo "Testing:"
	@echo " test            - Run all tests (backend + frontend + security)"
	@echo " test-backend    - Run only backend tests"
	@echo " test-frontend   - Run only frontend tests"
	@echo " test-security   - Run security tests with Snyk"
	@echo " test-quick      - Run backend tests without full rebuild"
	@echo ""
	@echo "Building:"
	@echo " build           - Build all Docker images"
	@echo " build-backend   - Build only backend services"
	@echo " build-frontend  - Build only frontend service"
	@echo " db-build        - Build database container"
	@echo ""
	@echo "Running:"
	@echo " up              - Start backend services only"
	@echo " up-full         - Start all services (backend + frontend)"
	@echo " up-backend      - Alias for 'up' (backend only)"
	@echo " down            - Stop all services"
	@echo " frontend        - Start frontend development server locally"
	@echo ""
	@echo "Development:"
	@echo " dev             - Install, lint, build, and start backend services"
	@echo " logs            - Show logs from running services"
	@echo " shell           - Open shell in backend container"
	@echo " clean           - Clean up Docker resources"
	@echo ""
	@echo "Production:"
	@echo " setup-certs     - Setup SSL certificates for Docker"
	@echo " setup-nginx     - Setup nginx configuration"
	@echo " prod-build      - Build production images"
	@echo " prod-up         - Start production services"
	@echo " prod-down       - Stop production services"
	@echo " prod-deploy     - Full production setup"
	@echo " prod-status     - Check production status"
	@echo " prod-logs       - Show production logs"

# Install dependencies
install:
	@echo "Installing dependencies..."
	@if [ -d "backend" ]; then \
		cd backend && pip install -r requirements.txt && pip install -r requirements-dev.txt; \
	fi
	@if [ -d "frontend" ]; then \
		cd frontend && \
		if [ ! -f "package-lock.json" ] || [ ! -d "node_modules" ]; then \
			echo "Running npm install (fresh install)..."; \
			npm install; \
		else \
			echo "Running npm ci (clean install)..."; \
			npm ci; \
		fi; \
	fi
	@echo "✅ Dependencies installed"

# Linting
lint:
	@echo "Running linting..."
	cd backend && black --check . && flake8 .
	@echo "Running frontend linting...";
	cd frontend && npm run lint:all;
	@echo "✅ Linting completed"

# Formatting
reformat:
	@echo "Formatting backend code..."
	cd backend && black . && flake8 .
	@echo "Formatting frontend code...";
	cd frontend && npm run format;
	@echo "✅ Code formatted"

# Run all tests
test: build
	@echo "Running all tests..."
	docker-compose run --rm tests
	@if [ -d "frontend" ]; then \
		docker-compose run --rm frontend-tests; \
	fi
	@echo "✅ All tests completed"

# Run only backend tests
test-backend: build-backend
	@echo "Running backend tests..."
	docker-compose run --rm tests
	@echo "✅ Backend tests completed"

# Run only frontend tests
test-frontend: build-frontend
	@echo "Running frontend tests..."
	@if [ -d "frontend" ]; then \
		docker-compose run --rm frontend-tests; \
	else \
		echo "Frontend directory not found, skipping frontend tests"; \
	fi
	@echo "✅ Frontend tests completed"

# Run security tests
test-security:
	@echo "Running security tests..."
	@if [ -z "$(SNYK_TOKEN)" ]; then \
		echo "Warning: SNYK_TOKEN not set, skipping security tests"; \
	else \
		docker-compose run --rm snyk-security; \
	fi
	@echo "✅ Security tests completed"

# Quick test (reuses existing images)
test-quick:
	@echo "Running quick tests..."
	docker-compose run --rm tests
	@echo "✅ Quick tests completed"

# Build all Docker images
build:
	@echo "Building all Docker images..."
	docker-compose build api db-init frontend
	@echo "✅ All Docker images built"

# Build only backend services
build-backend:
	@echo "Building backend services..."
	docker-compose build api db-init
	@echo "✅ Backend services built"

# Build only frontend service
build-frontend:
	@echo "Building frontend service..."
	docker-compose build frontend
	@echo "✅ Frontend service built"

# Start services (backend only for development)
up:
	@echo "Initializing database..."
	docker-compose up db-init
	@echo "Starting API service..."
	docker-compose up -d api
	@echo "✅ Backend services started"

# Start all services including frontend
up-full:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "✅ All services started"

# Alias for up (backend only)
up-backend: up

# Stop all services
down:
	@echo "Stopping all services..."
	docker-compose down
	@echo "✅ All services stopped"

# Show logs
logs:
	docker-compose logs -f

# Shell into backend container
shell:
	docker-compose exec api /bin/bash

# Cleanup
clean:
	docker system prune -f
	docker volume prune -f
	@echo "✅ Cleanup completed"

# Build database
db-build:
	@echo "Building database..."
	docker-compose build db-init
	@echo "✅ Database built"

# Start frontend development server locally
frontend:
	@echo "Starting frontend development server..."
	@if [ -d "frontend" ] && [ -d "frontend/node_modules" ]; then \
		cd frontend && npm start; \
	else \
		echo "Frontend not found or dependencies not installed. Run 'make install' first."; \
		exit 1; \
	fi

# Development workflow (backend focused since frontend is deprecated)
dev: install lint build-backend up
	@echo "✅ Development environment ready! Backend running on http://localhost:8000"
	@echo "To start frontend: make frontend"

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

# Setup nginx configuration
setup-nginx:
	@echo "Setting up nginx configuration..."
	sudo cp nginx/voxify.conf /etc/nginx/sites-available/voxify
	sudo ln -sf /etc/nginx/sites-available/voxify /etc/nginx/sites-enabled/
	sudo rm -f /etc/nginx/sites-enabled/default
	sudo nginx -t
	sudo systemctl restart nginx
	sudo systemctl enable nginx
	@echo "✅ Nginx configured and running"

# Production targets
prod-build:
	@echo "Building production images..."
	docker-compose -f docker-compose.prod.yml build
	@echo "✅ Production images built"

prod-up:
	@echo "Starting production services..."
	@if [ ! -f ".env.prod" ]; then \
		echo "❌ Error: .env.prod file not found!"; \
		echo "Please copy .env.prod.example to .env.prod and fill in your values"; \
		exit 1; \
	fi
	docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
	@echo "✅ Production services started"

prod-down:
	@echo "Stopping production services..."
	docker-compose -f docker-compose.prod.yml down
	@echo "✅ Production services stopped"

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

# Full production setup
prod-deploy: setup-nginx prod-build prod-up
	@echo "✅ Production deployment complete!"
	@echo "Your API is now available at: https://milaniez-montagy.duckdns.org"

# Check production status
prod-status:
	@echo "=== Nginx Status ==="
	sudo systemctl status nginx --no-pager -l
	@echo ""
	@echo "=== Production Services Status ==="
	docker-compose -f docker-compose.prod.yml ps
	@echo ""
	@echo "=== SSL Certificate Status ==="
	sudo certbot certificates