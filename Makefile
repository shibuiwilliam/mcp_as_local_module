DIR := $(shell pwd)
GIT_COMMIT := $(shell git rev-parse HEAD)

SRC := $(DIR)/
TEST := $(DIR)/tests

.PHONY: lint
lint:
	uvx ruff check --extend-select I --fix $(SRC)

.PHONY: fmt
fmt:
	uvx ruff format $(SRC)

.PHONY: lint_fmt
lint_fmt: lint fmt
