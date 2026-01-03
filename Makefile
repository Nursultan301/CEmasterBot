# =========================
# i18n / gettext settings
# =========================

PYTHON        ?= python
PYBABEL       ?= pybabel

SRC_DIR       := src
I18N_DIR      := src/core/i18n
LOCALES_DIR   := $(I18N_DIR)/locales
DOMAIN        := message
LANGS         := ru ky en

BABEL_CFG     := babel.cfg
POT_FILE      := $(LOCALES_DIR)/messages.pot


# =========================
# Help
# =========================
.PHONY: help
help:
	@echo "i18n commands:"
	@echo "  make i18n-extract   - extract msgids to messages.pot"
	@echo "  make i18n-init      - create .po files (first time)"
	@echo "  make i18n-update    - update existing .po files"
	@echo "  make i18n-compile   - compile .po -> .mo"
	@echo "  make i18n-clean     - remove compiled .mo files"
	@echo "  make i18n-check     - check translations consistency"


# =========================
# Extract strings
# =========================
.PHONY: i18n-extract
i18n-extract:
	@echo "Extracting translations..."
	$(PYBABEL) extract -F $(BABEL_CFG) -o $(POT_FILE) .


# =========================
# Init languages (only once)
# =========================
.PHONY: i18n-init
i18n-init: i18n-extract
	@for lang in $(LANGS); do \
		if [ ! -f "$(LOCALES_DIR)/$$lang/LC_MESSAGES/$(DOMAIN).po" ]; then \
			echo "Init language $$lang"; \
			$(PYBABEL) init \
				-i $(POT_FILE) \
				-d $(LOCALES_DIR) \
				-D $(DOMAIN) \
				-l $$lang ; \
		else \
			echo "Language $$lang already exists, skipping"; \
		fi \
	done


# =========================
# Update existing .po
# =========================
.PHONY: i18n-update
i18n-update: i18n-extract
	@echo "Updating translations..."
	$(PYBABEL) update \
		-i $(POT_FILE) \
		-d $(LOCALES_DIR) \
		-D $(DOMAIN)


# =========================
# Compile .po -> .mo
# =========================
.PHONY: i18n-compile
i18n-compile:
	@echo "Compiling translations..."
	$(PYBABEL) compile \
		-d $(LOCALES_DIR) \
		-D $(DOMAIN)


# =========================
# Clean compiled files
# =========================
.PHONY: i18n-clean
i18n-clean:
	@echo "Cleaning compiled translations..."
	@find $(LOCALES_DIR) -name "*.mo" -delete


# =========================
# Check translations
# =========================
.PHONY: i18n-check
i18n-check:
	@echo "Checking translations..."
	$(PYBABEL) compile \
		-d $(LOCALES_DIR) \
		-D $(DOMAIN) \
		--statistics


.PHONY: lint
lint:
	ruff check src/ --fix
	black src/

.PHONY: format
format:
	black src/
	ruff format src/

.PHONY: check
chack:
	ruff check src/
