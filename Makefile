.PHONY: install marketplaces plugins list uninstall

# Marketplaces: name -> github repo
MARKETPLACES := \
	anthropics/claude-plugins-official \
	JuliusBrussee/caveman \
	citedy/claude-plugins

# Plugins: plugin@marketplace
PLUGINS := \
	caveman@caveman \
	game-sounds@citedy \
	frontend-design@claude-plugins-official \
	context7@claude-plugins-official \
	code-review@claude-plugins-official \
	github@claude-plugins-official

install: marketplaces plugins ## Add marketplaces then install all plugins

marketplaces: ## Add all marketplaces
	@for m in $(MARKETPLACES); do \
		echo ">> marketplace add $$m"; \
		claude plugin marketplace add $$m || true; \
	done

plugins: ## Install all plugins
	@for p in $(PLUGINS); do \
		echo ">> install $$p"; \
		claude plugin install $$p || true; \
	done

list: ## Show installed plugins
	@claude plugin list

uninstall: ## Uninstall all listed plugins
	@for p in $(PLUGINS); do \
		echo ">> uninstall $$p"; \
		claude plugin uninstall $$p || true; \
	done
