# Define variables
APP_DIR = api
APP = $(APP_DIR)/app.py
VENV = venv
PYTHON = $(VENV)/bin/python

# Help function to display available commands
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

run: ## Run the Fastapi app from the api directory
	@if [ ! -f $(PYTHON) ]; then \
		echo "Virtual environment not found. Please run 'make install' first."; \
		exit 1; \
	fi
	$(PYTHON) api/app.py


install: ## Install dependencies and create virtual environment if not present
	@if [ ! -d $(VENV) ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv $(VENV); \
	fi
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	$(VENV)/bin/pre-commit install

test: ## Run pytest on api dir
	pytest api/

fix: ## Black format and isort on api dir
	black api/
	isort api/

clean: ## Clean up Python bytecode files and caches
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

no_verify_commit:
	@read -p "Enter commit message: " msg; \
	git commit -a -m "$$msg" --no-verify
	git push

.PHONY: run install clean
