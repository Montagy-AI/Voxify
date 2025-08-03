# Voxify Project Makefile
.PHONY: help install lint reformat test test-quick build up down clean dev logs shell \
        db-build frontend setup-certs setup-nginx backend-prod prod-deploy prod-status

# Default target
help:
	@echo "Available targets:"
	@echo " install         - Install all dependencies"
	@echo " lint            - Run linting for backend"
	@echo " reformat        - Reformat code for backend"
	@echo " test            - Run full test suite with Docker"
	@echo " test-quick      - Run tests without full Docker rebuild"
	@echo " build           - Build Docker images"
	@echo " up              - Start services with docker-compose"
	@echo " down            - Stop backend services"
	@echo " logs            - Show logs from running services"
	@echo " shell           - Open shell in backend container"
	@echo " clean           - Clean up Docker resources"
	@echo " dev             - Install, lint, build, and start services"
	@echo " db-build        - Build database container"
	@echo " frontend		- Start frontend development server"
	@echo " Production:"
	@echo ""
	@echo " setup-certs     - Setup SSL certificates for Docker"
	@echo " setup-nginx     - Setup nginx configuration"
	@echo " backend-prod    - Start backend for production"
	@echo " prod-deploy     - Full production setup"
	@echo " prod-status     - Check production status"

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
	@echo "✅ Linting completed"

# Formatting
reformat:
	@echo "Formatting code..."
	cd backend && black .
	@echo "✅ Code formatted"

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

# Build Docker images
build:
	@echo "Building backend services..."
	docker-compose build api
	@echo "✅ Backend services built"

# Start services
up:
	@echo "Initializing database..."
	docker-compose up db-init
	@echo "Starting API service..."
	docker-compose up -d api
	@echo "✅ Services started"

# Stop services
down:
	@echo "Stopping backend services..."
	docker-compose down
	@echo "✅ Backend services stopped"

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

# Start frontend development server
frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm start
	@echo "✅ Frontend server running on http://localhost:3000"

# Development workflow
dev: install lint build up frontend
	@echo "✅ Development environment ready!"

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

# Production backend with nginx handling SSL
backend-prod:
	@echo "Starting backend for production."
	docker-compose up -d api
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