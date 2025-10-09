build:
	@if [ "$$(uname -s)" = "Darwin" ]; then \
		echo "Building on macOS..."; \
		sed -i '' 's/^version = .*/version = "$(v)"/' pyproject.toml; \
		sed -i '' 's/__version__ = .*/__version__ = "$(v)"/' spai/__init__.py; \
	else \
		echo "Building on Linux..."; \
		sed -i 's/^version = .*/version = "$(v)"/' pyproject.toml; \
		sed -i 's/__version__ = .*/__version__ = "$(v)"/' spai/__init__.py; \
	fi
	rm -rf dist
	uv build

publish:
	uv publish --username "__token__" --password $(token)

