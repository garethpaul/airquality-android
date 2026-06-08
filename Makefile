PYTHON ?= python3
GRADLE ?= ./gradlew

.PHONY: lint test build verify check

lint:
	$(PYTHON) -m py_compile scripts/check_airquality_android_contracts.py

test:
	$(PYTHON) scripts/check_airquality_android_contracts.py

build:
	@if [ -n "$$ANDROID_HOME" ] || [ -f local.properties ]; then \
		$(GRADLE) lint test assembleDebug --no-daemon; \
	else \
		echo "Android SDK not configured; skipping Gradle build"; \
	fi

verify: lint test

check: verify build
