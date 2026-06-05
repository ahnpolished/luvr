.PHONY: install run test lint format clean smoke-test setup

# Default Python
PYTHON := python3
VENV := .venv

install:
	@echo "🔧 Installing Luvr..."
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install -e ".[dev]"
	@echo "✅ Installation complete!"
	@echo "   Run 'cp .env.example .env' and edit .env with your API keys."
	@echo "   Then run 'make run' to start the server."

run:
	@echo "🚀 Starting Luvr server..."
	. $(VENV)/bin/activate && uvicorn src.server:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "🧪 Running tests..."
	. $(VENV)/bin/activate && pytest

test-cov:
	@echo "🧪 Running tests with coverage..."
	. $(VENV)/bin/activate && pytest --cov=src --cov-report=html

lint:
	@echo "🔍 Linting..."
	. $(VENV)/bin/activate && ruff check src/ tests/

format:
	@echo "🎨 Formatting..."
	. $(VENV)/bin/activate && ruff format src/ tests/

clean:
	@echo "🧹 Cleaning up..."
	rm -rf $(VENV) .pytest_cache .ruff_cache .mypy_cache htmlcov dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

smoke-test:
	@echo "💨 Running smoke tests..."
	. $(VENV)/bin/activate && python scripts/smoke_test.py

setup:
	@echo "🛠️  Running setup script..."
	bash scripts/setup.sh
