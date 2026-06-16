PYTHON ?= python3
override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
GRADLE ?= $(ROOT)/gradlew
CHECK_SCRIPT := $(ROOT)/scripts/check_airquality_android_contracts.py

.PHONY: lint test build verify check

lint:
	$(PYTHON) -m py_compile "$(CHECK_SCRIPT)"

test:
	$(PYTHON) "$(CHECK_SCRIPT)"

build:
	@if [ -n "$$ANDROID_HOME" ] || [ -f "$(ROOT)/local.properties" ]; then \
		cd "$(ROOT)" && "$(GRADLE)" lint test assembleDebug --no-daemon && \
		$(PYTHON) "$(CHECK_SCRIPT)"; \
	else \
		echo "Android SDK not configured; skipping Gradle build"; \
	fi

verify: lint test

check: verify build
