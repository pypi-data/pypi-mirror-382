.PHONY: release
release:
	@kind=$${KIND:-patch}; \
	uv version --bump $$kind; \
	v=$$(uv version); \
	git add pyproject.toml; \
	git commit -m "chore: release v$$v"; \
	git tag "v$$v"; \
	git push origin HEAD; \
	git push origin "v$$v"; \
	echo "Released v$$v"

# Usage:
#   make release              # defaults to patch
#   KIND=minor make release
#   KIND=major make release
