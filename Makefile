.PHONY: help install test run-stdio run-http docker-build docker-run docker-stop clean lint format

help:
	@echo "Weather MCP Server - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install      - Install Python dependencies"
	@echo "  make test         - Run test suite"
	@echo "  make lint         - Run code linting"
	@echo "  make format       - Format code with black"
	@echo ""
	@echo "Running:"
	@echo "  make run-stdio    - Run server with STDIO transport"
	@echo "  make run-http     - Run server with HTTP transport"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run with docker-compose"
	@echo "  make docker-stop  - Stop docker containers"
	@echo "  make docker-logs  - View container logs"
	@echo "  make docker-clean - Remove containers and images"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Remove temporary files"

install:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio black flake8 mypy

test:
	pytest tests/ -v --cov=weather_mcp --cov-report=html

lint:
	flake8 weather_mcp/ tests/ --max-line-length=100
	mypy weather_mcp/

format:
	black weather_mcp/ tests/ --line-length=100

run-stdio:
	python server.py --stdio

run-http:
	python server.py --http

docker-build:
	docker build -t weather-mcp-server:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v --rmi all

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf htmlcov/ .coverage
