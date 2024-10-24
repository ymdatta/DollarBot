# Define variables
PYTHON_VERSION = 3.12.1
VENV_NAME = mm_venv
PYENV_ROOT = $(HOME)/.pyenv

# Help function to display available commands
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install_pyenv: ## Check if pyenv is installed, install if not
	@if ! command -v pyenv > /dev/null 2>&1; then \
		echo "pyenv not installed. Installing pyenv..."; \
		rm -rf ~/.pyenv; \
		curl https://pyenv.run | bash; \
		echo 'export PYENV_ROOT="$(PYENV_ROOT)"' >> $(HOME)/.bashrc; \
		echo 'export PATH="$(PYENV_ROOT)/bin:$$PATH"' >> $(HOME)/.bashrc; \
		echo 'eval "$$(pyenv init --path)"' >> $(HOME)/.bashrc; \
		echo 'eval "$$(pyenv init -)"' >> $(HOME)/.bashrc; \
		echo 'eval "$$(pyenv virtualenv-init -)"' >> $(HOME)/.bashrc; \
		echo "Please run 'source ~/.bashrc' or restart your terminal for changes to take effect."; \
	else \
		echo "pyenv is already installed."; \
	fi

check_python: ## Install Python 3.12.1 using pyenv if not installed
	@if ! pyenv versions --bare | grep -q $(PYTHON_VERSION); then \
		echo "Python $(PYTHON_VERSION) not found. Installing..."; \
		pyenv install $(PYTHON_VERSION); \
	else \
		echo "Python $(PYTHON_VERSION) is already installed."; \
	fi
	@pyenv local $(PYTHON_VERSION)

create_venv: check_python ## Create and activate virtual environment mm_venv
	@if [ ! -d "$(PYENV_ROOT)/versions/$(VENV_NAME)" ]; then \
		echo "Creating virtual environment $(VENV_NAME)..."; \
		pyenv virtualenv $(PYTHON_VERSION) $(VENV_NAME); \
	else \
		echo "Virtual environment $(VENV_NAME) already exists."; \
	fi
	@pyenv local $(VENV_NAME)

install: create_venv ## Install dependencies in the virtual environment
	@pyenv exec pip install --upgrade pip
	@pyenv exec pip install -r requirements.txt
	@pyenv exec pre-commit install
	@echo "export PYTHONPATH=$(shell pwd):\$$PYTHONPATH" >> ~/.bashrc
	@echo "PYTHONPATH exported to .bashrc. Please restart your terminal or run 'source ~/.bashrc' to apply changes."


run: ## Run the FastAPI app using the virtual environment
	@pyenv exec python api/app.py

test: ## Start MongoDB Docker container, run tests, and clean up
	@echo "Starting MongoDB Docker container..."
	@docker run --name mongo-test -p 27017:27017 -d mongo:latest
	@sleep 5  # Wait for MongoDB to be ready
	@echo "Running tests..."
	@pyenv exec pytest || (docker stop mongo-test && docker rm mongo-test && exit 1)
	@echo "Stopping and removing Docker container..."
	@docker stop mongo-test
	@docker rm mongo-test

fix: ## Black format and isort on api dir
	@pyenv exec black api/
	@pyenv exec isort api/

clean: ## Clean up Python bytecode files and caches
	@docker stop mongo-test || true
	@docker rm mongo-test || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

no_verify_push: ## Stage, commit & push with --no-verify
	@read -p "Enter commit message: " msg; \
	git commit -a -m "$$msg" --no-verify
	git push

.PHONY: help install run test fix clean no_verify_push
