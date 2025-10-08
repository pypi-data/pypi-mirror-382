build:
	rm -rf dist
	uv build

publish:
	rm -rf dist
	uv build
	uv run python -m twine upload dist/*

inspector:
	npx @modelcontextprotocol/inspector