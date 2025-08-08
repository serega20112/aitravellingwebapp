ifeq ($(OS),Windows_NT)
	PROJECT_DIR := $(shell cd && cd .. && pwd)
else
	PROJECT_DIR := $(shell pwd)
endif
COMPOSE = docker compose -f build/docker-compose.yml --project-directory $(PROJECT_DIR)

.PHONY: up down logs build lint test restart

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

restart: down up

logs:
	$(COMPOSE) logs -f

build:
	$(COMPOSE) build

lint:
	echo "Install lint and typing tools"
	python -m pip install -q black isort flake8 flake8-annotations flake8-docstrings mypy fastapi

	echo "Check black"
	black --check src/

	echo "Check isort"
	isort --check-only --profile black src/

	@echo "Check flake8"
	flake8 src/

#	echo "Run mypy for typing"
#	mypy src/ --strict

fix:
	echo "==> Running code formatting (isort + black)"
	isort --profile black src
	black src
test:
	python -m pip install -q pytest httpx
	pytest -q