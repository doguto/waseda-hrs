SQLC_DIR := sqlc
DB_HOST ?= localhost
DB_PORT ?= 5432
DB_NAME ?= hrs
DB_USER ?= postgres
DB_PASSWORD ?= password
GO ?= go
# Prefer an installed binary for fast local generation. CI and fresh environments
# fall back to the version pinned by sqlc/go.mod.
SQLC ?= $(shell command -v sqlc 2>/dev/null || echo "$(GO) tool sqlc")

.PHONY: fmt
fmt:
	uv run --all-packages ruff format .
	uv run --all-packages ruff check . --fix

.PHONY: lint
lint:
	uv run --all-packages ruff format . --check
	uv run --all-packages ruff check .

.PHONY: typecheck
typecheck:
	uv run --all-packages mypy packages

.PHONY: test
test:
	@uv run --all-packages pytest; status=$$?; \
	if [ $$status -ne 0 ] && [ $$status -ne 5 ]; then exit $$status; fi

.PHONY: check
check: lint typecheck test

.PHONY: sqlc
sqlc:
	@echo "Running sqlc via: $(SQLC)"
	cd $(SQLC_DIR) && $(SQLC) generate -f sqlc.yaml

.PHONY: dry-migrate
dry-migrate:
	cd $(SQLC_DIR) && PGPASSWORD=$(DB_PASSWORD) $(GO) tool psqldef \
		-h $(DB_HOST) -U $(DB_USER) -p $(DB_PORT) $(DB_NAME) \
		--dry-run < schema.sql

.PHONY: migrate
migrate:
	cd $(SQLC_DIR) && PGPASSWORD=$(DB_PASSWORD) $(GO) tool psqldef \
		-h $(DB_HOST) -U $(DB_USER) -p $(DB_PORT) $(DB_NAME) \
		< schema.sql
