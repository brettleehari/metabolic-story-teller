# Makefile for GlucoLens Backend
# Provides convenient commands for development, testing, and deployment validation

.PHONY: help install test lint type-check security-check static-analysis deployment-check clean

# Default target
help:
	@echo "GlucoLens Backend - Available Commands:"
	@echo ""
	@echo "  make install              Install all dependencies"
	@echo "  make test                 Run all tests"
	@echo "  make test-deployment      Run deployment readiness tests"
	@echo "  make lint                 Run code linting (pylint)"
	@echo "  make type-check           Run type checking (mypy)"
	@echo "  make security-check       Run security analysis (bandit)"
	@echo "  make static-analysis      Run all static analysis tools"
	@echo "  make deployment-check     Run full deployment validation"
	@echo "  make format               Format code with black and isort"
	@echo "  make clean                Clean up temporary files"
	@echo ""

# Install dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt

# Run all tests
test:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Run deployment readiness tests
test-deployment:
	@echo "Running deployment readiness tests..."
	pytest tests/test_deployment.py -v --tb=short

# Run pylint
lint:
	@echo "Running pylint..."
	pylint app/ --rcfile=.pylintrc || true

# Run mypy type checking
type-check:
	@echo "Running mypy type checking..."
	mypy --config-file=mypy.ini || true

# Run bandit security check
security-check:
	@echo "Running bandit security analysis..."
	bandit -r app/ -c .bandit || true

# Run all static analysis tools
static-analysis: lint type-check security-check
	@echo ""
	@echo "Static analysis complete!"

# Format code
format:
	@echo "Formatting code with black..."
	black app/ tests/
	@echo "Sorting imports with isort..."
	isort app/ tests/

# Full deployment validation
deployment-check: static-analysis test-deployment
	@echo ""
	@echo "==========================================="
	@echo "Deployment Validation Complete!"
	@echo "==========================================="
	@echo ""
	@echo "Next steps:"
	@echo "  1. Review any warnings from static analysis"
	@echo "  2. Ensure all tests passed"
	@echo "  3. Check Docker images build successfully"
	@echo "  4. Test deployment in staging environment"
	@echo ""

# Clean up temporary files
clean:
	@echo "Cleaning up temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"

# Check Python version
check-python:
	@python --version | grep "Python 3.11" || (echo "Error: Python 3.11 required" && exit 1)

# Validate requirements.txt
check-requirements:
	@echo "Validating requirements.txt..."
	pip check

# Build Docker image locally
docker-build:
	@echo "Building Docker image..."
	docker build -t glucolens-backend:latest .

# Run Docker container locally
docker-run: docker-build
	@echo "Running Docker container..."
	docker run --rm -p 8000:8000 \
		-e DATABASE_URL=postgresql://glucolens:password@host.docker.internal:5432/glucolens \
		-e REDIS_URL=redis://host.docker.internal:6379/0 \
		-e SECRET_KEY=dev-secret-key \
		glucolens-backend:latest
