# Voxify Project Makefile
.PHONY: help install lint reformat test test-quick build up down clean dev logs shell \
        db-build frontend setup-certs setup-nginx prod-deploy prod-status

# Default target
help:
	@echo "Available targets:"
	@echo " install         - Install all backend dependencies"
	@echo " build           - Build Docker images"
	@echo " up              - Start services with docker-compose"
	@echo " down            - Stop backend services"
	@echo " logs            - Show logs from running services"
	@echo " shell           - Open shell in backend container"
	@echo " clean           - Clean up Docker resources"
	@echo " dev             - Install, lint, build, and start services"
	@echo " db-build        - Build database container"
	@echo " frontend        - Start frontend development server"
	@echo " "
	@echo " Testing:"
	@echo " lint            - Run linting for backend"
	@echo " reformat        - Reformat code for backend"
	@echo " test            - Run full test suite with Docker"
	@echo " test-quick      - Run tests without full Docker rebuild"
	@echo ""
	@echo " Production:"
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