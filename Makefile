DOCKER_COMPOSE=docker-compose
DOCKER_IMAGE=app

# Default target
.PHONY: help
help:  ## Display this help
	@echo "Usage: make [target] ..."
	@echo
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { printf "  %-15s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: build

build:  ## Build the Docker image
	$(DOCKER_COMPOSE) build

.PHONY: up
up:  ## Start the Docker Compose services
	$(DOCKER_COMPOSE) up -d

.PHONY: down
down:  ## Stop the Docker Compose services
	$(DOCKER_COMPOSE) down

.PHONY: logs
logs:  ## Tail the logs of the Docker Compose services
	$(DOCKER_COMPOSE) logs -f

.PHONY: shell
shell:  ## Get a shell inside the app container
	$(DOCKER_COMPOSE) exec app /bin/bash

.PHONY: migrate
migrate:  ## Run Alembic database migrations
	$(DOCKER_COMPOSE) exec app alemic upgrade head

.PHONY: test
test:  ## Run Django tests
	$(DOCKER_COMPOSE) exec app pytest tests -v

.PHONY: clean
clean:  ## Clean up unused Docker resources
	docker system prune -f
