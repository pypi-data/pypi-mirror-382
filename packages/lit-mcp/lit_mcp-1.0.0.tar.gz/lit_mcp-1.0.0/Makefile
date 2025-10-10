.PHONY: release
release:
	@kind=$${KIND:-patch}; \
	uv version --bump $$kind; \
	v=$$(uv version | awk '{print $$NF}'); \
	git add pyproject.toml; \
	git commit -m "chore: release v$$v"; \
	git tag "v$$v"; \
	git push origin HEAD; \
	git push origin "v$$v"; \
	echo "✅ Released v$$v"
