.PHONY: help install build clean test lint dev dist all

PYTHON := python3
POETRY := poetry
PIP := pip
PARALLEL := $(shell nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 1)

help:
	@echo "Available commands:"
	@echo "  make install   - Install dependencies using poetry or pip"
	@echo "  make build     - Build the application"
	@echo "  make clean     - Clean build artifacts"
	@echo "  make test      - Run tests"
	@echo "  make lint      - Run linters"
	@echo "  make dev       - Install development dependencies"
	@echo "  make dist      - Create distribution packages"

install:
	@if command -v $(POETRY) >/dev/null 2>&1; then \
		$(POETRY) install; \
	else \
		$(PIP) install -r requirements.txt; \
	fi

build:
	@if command -v $(POETRY) >/dev/null 2>&1; then \
		$(POETRY) run python build.py && \
		$(POETRY) run pyinstaller url-markdown.spec; \
	else \
		python build.py && \
		pyinstaller url-markdown.spec; \
	fi

build-x86_64:
	ARCHFLAGS="-arch x86_64" make build

build-arm64:
	ARCHFLAGS="-arch arm64" make build

dev:
	@if command -v $(POETRY) >/dev/null 2>&1; then \
		$(POETRY) install --with dev; \
	else \
		$(PIP) install -r requirements-dev.txt; \
	fi

test:
	@if command -v $(POETRY) >/dev/null 2>&1; then \
		$(POETRY) run pytest; \
	else \
		pytest; \
	fi

lint:
	@if command -v $(POETRY) >/dev/null 2>&1; then \
		$(POETRY) run flake8 && $(POETRY) run mypy .; \
	else \
		flake8 && mypy .; \
	fi

dist:
	@if command -v $(POETRY) >/dev/null 2>&1; then \
		$(POETRY) build; \
	else \
		$(PYTHON) setup.py sdist bdist_wheel; \
	fi

clean:
	rm -rf build/ dist/ *.spec __pycache__/ */__pycache__/

all: clean install build test lint dist
	@echo "All steps completed successfully."