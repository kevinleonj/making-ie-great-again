.PHONY: install lint format typecheck test test-unit test-integration test-e2e frontend backend all

install:
	pip install -e ".[dev,tts,audio]"
	playwright install chromium

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .
	ruff check --fix .

typecheck:
	mypy frontend/ backend/

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-e2e:
	pytest tests/e2e/ -v --headed

test: test-unit test-integration

frontend:
	python -m frontend.main

backend:
	uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

all:
	@echo "Run 'make backend' in one terminal, 'make frontend' in another"
