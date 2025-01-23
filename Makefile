# project directories
SRC_DIR := src
LOCALES_DIR := locales
LANGUAGES := $(shell find $(LOCALES_DIR) -mindepth 1 -maxdepth 1 -type d -exec basename {} \;)
POT_FILE := $(LOCALES_DIR)/base.pot

# python file patterns
PYTHON_FILES := $(shell find $(SRC_DIR) -name '*.py')

# makefile targets
GETTEXT_FUNCTION := get_str
NGETTEXT_FUNCTION := nget_str
BUG_REPORT_ADDRESS := Francesco146@users.noreply.github.com

.PHONY: all update-pot update-po compile clean help

all: update-pot update-po compile

# extract translatable strings and update the POT file
update-pot:
	xgettext \
		--language=Python \
		--keyword=$(GETTEXT_FUNCTION) \
		--keyword=$(NGETTEXT_FUNCTION):1,2 \
		--output=$(POT_FILE) \
		--msgid-bugs-address=$(BUG_REPORT_ADDRESS) \
		$(PYTHON_FILES)

update-po: $(foreach lang,$(LANGUAGES),$(LOCALES_DIR)/$(lang)/LC_MESSAGES/base.po)
$(LOCALES_DIR)/%/LC_MESSAGES/base.po: $(POT_FILE)
	msgmerge --update --no-fuzzy-matching --backup=none $@ $(POT_FILE)

# compile the PO files into MO files for all languages
compile: $(foreach lang,$(LANGUAGES),$(LOCALES_DIR)/$(lang)/LC_MESSAGES/base.mo)
$(LOCALES_DIR)/%/LC_MESSAGES/base.mo: $(LOCALES_DIR)/%/LC_MESSAGES/base.po
	msgfmt $< --output-file=$@

clean: 
	rm -f $(foreach lang,$(LANGUAGES),$(LOCALES_DIR)/$(lang)/LC_MESSAGES/*.mo)
	rm -f $(POT_FILE)

help:
	@echo "Available targets:"
	@echo "  all             - Run all steps: update-pot, update-po, and compile"
	@echo "  update-pot      - Extract translatable strings and update the POT file"
	@echo "  update-po       - Update the PO files for all languages using msgmerge"
	@echo "  compile         - Compile the PO files into MO files for all languages"
	@echo "  clean           - Remove compiled MO files and backups"
	@echo "  help            - Display this help message"
