.PHONY: install dev test lint clean migration migrate docker-build docker-run docker-stop test-api test-connectivity

# Install dependencies
install:
	pip install -r requirements.txt

# Run development server
dev:
	python run.py

# Run tests
test:
	pytest

# Run API connectivity tests
test-api:
	python -m tests.utils.test_openai_connectivity

# Run service connectivity tests
test-connectivity:
	python -m tests.utils.test_mock_connectivity

# Run linting
lint:
	flake8 app tests

# Clean build artifacts
clean:
	rm -rf __pycache__ .pytest_cache
	find . -name "*.pyc" -delete

# Create a new migration
migration:
	alembic revision --autogenerate -m "$(message)"

# Run migrations
migrate:
	alembic upgrade head

# Build Docker image
docker-build:
	docker-compose build

# Run with Docker Compose
docker-run:
	docker-compose up

# Stop Docker containers
docker-stop:
	docker-compose down

# Help
help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev           - Run development server"
	@echo "  make test          - Run tests"
	@echo "  make test-api      - Run API connectivity tests"
	@echo "  make test-connectivity - Run service connectivity tests"
	@echo "  make lint          - Run linting"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make migration     - Create a new migration (usage: make migration message='migration description')"
	@echo "  make migrate       - Run migrations"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run with Docker Compose"
	@echo "  make docker-stop   - Stop Docker containers"

# Default target
default: help 