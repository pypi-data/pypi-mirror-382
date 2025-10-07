check: format lint typecheck

format:
	uv run black . --check --diff

lint:
	uv run ruff check .

typecheck:
	uv run pyright

publish:
	scripts/publish.py

.PHONY: check format lint typecheck