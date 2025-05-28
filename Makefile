install:
	uv sync

lint:
	uv run flake8 page_loader tests

test:
	uv run pytest -vv -s --capture=tee-sys --log-cli-level=DEBUG

cover:
	uv run pytest --cov

build:
	uv run hatch build

package-install:
	uv tool install --force dist/*.whl

run:
	uv run page-loader https://ru.hexlet.io/courses

.PHONY: install lint test build package-install run
