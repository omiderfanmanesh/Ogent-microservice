.PHONY: help install setup dev lint format test docker-build docker-up docker-down clean

PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
VENV := venv
VENV_BIN := $(VENV)/bin

help:
	@echo "Ogent - LangChain Agent Service"
	@echo ""
	@echo "Usage:"
	@echo "  make help                 Show this help message"
	@echo "  make install              Install development dependencies"
	@echo "  make setup                Set up the project (create venv, install dependencies, initialize database)"
	@echo "  make dev                  Run the development server"
	@echo "  make lint                 Run linters (black, isort, mypy)"
	@echo "  make format               Format code with black and isort"
	@echo "  make test                 Run tests"
	@echo "  make docker-build         Build Docker image"
	@echo "  make docker-up            Start services with Docker Compose"
	@echo "  make docker-down          Stop Docker Compose services"
	@echo "  make clean                Clean build artifacts and cache"

install:
	$(PIP) install -r requirements.txt

setup:
	$(PYTHON) -m venv $(VENV)
	$(VENV_BIN)/pip install --upgrade pip
	$(VENV_BIN)/pip install -r requirements.txt
	cp -n .env.example .env || true
	@echo "Setup complete! Remember to edit .env with your settings."
	@echo "To activate the virtual environment, run: source $(VENV)/bin/activate"

dev:
	$(PYTHON) run.py

lint:
	black --check app
	isort --check-only app
	mypy app

format:
	black app
	isort app

test:
	$(PYTEST)

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf app/__pycache__
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete 