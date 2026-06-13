#!/usr/bin/env python3
"""Static contracts for the legacy AirQuality Android project."""

import hashlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"

EXPECTED_CI_WORKFLOW = """name: Check

on:
  pull_request:
  push:
    branches:
      - master
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: check-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  check:
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.12", "3.14"]
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Set up Python
        uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0
        with:
          python-version: ${{ matrix.python-version }}
      - name: Run SDK-free repository verification
        run: make check
        env:
          ANDROID_HOME: ""
          ANDROID_SDK_ROOT: ""

  android:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Install Android SDK packages
        run: '\"${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager\" \"platform-tools\" \"platforms;android-22\" \"build-tools;24.0.3\"'
      - name: Set up Java 8
        uses: actions/setup-java@be666c2fcd27ec809703dec50e508c2fdc7f6654 # v5.2.0
        with:
          distribution: corretto
          java-version: "8"
      - name: Run full Android verification
        run: make check
"""

EXPECTED_WRAPPER_PROPERTIES = """distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionSha256Sum=1d7c28b3731906fd1b2955946c1d052303881585fc14baedd675e4cf2bc1ecab
distributionUrl=https\\://services.gradle.org/distributions/gradle-2.2.1-all.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
"""


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def sha256(relative_path):
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def manifest_permissions():
    manifest = ET.parse(ROOT / "app/src/main/AndroidManifest.xml").getroot()
    return [
        item.attrib.get(ANDROID_NS + "name")
        for item in manifest.findall("uses-permission")
    ]


def main():
    failures = []

    network = read_text("app/src/main/java/twitterdev/airquality/NetworkRequest.java")
    main_activity = read_text("app/src/main/java/twitterdev/airquality/MainActivity.java")
    login_activity = read_text("app/src/main/java/twitterdev/airquality/LoginActivity.java")
    network_tests = read_text("app/src/test/java/twitterdev/airquality/NetworkRequestTest.java")
    app_build = read_text("app/build.gradle")
    application = read_text("app/src/main/java/twitterdev/airquality/AirQualityApplication.java")
    manifest = read_text("app/src/main/AndroidManifest.xml")
    sensor_plan = read_text("docs/plans/2026-06-09-main-activity-sensor-lifecycle-guard.md")
    editor_metadata_plan = read_text("docs/plans/2026-06-09-editor-metadata-ignore.md")
    backup_plan = read_text("docs/plans/2026-06-09-android-backup-opt-out.md")
    ci_plan = read_text("docs/plans/2026-06-10-ci-baseline.md")
    response_limit_plan = read_text(
        "docs/plans/2026-06-10-network-response-size-limit.md"
    )
    nonblocking_request_plan = read_text(
        "docs/plans/2026-06-10-main-activity-nonblocking-request.md"
    )
    request_lifecycle_plan = read_text(
        "docs/plans/2026-06-12-main-activity-request-lifecycle.md"
    )
    wrapper_plan = read_text("docs/plans/2026-06-12-gradle-wrapper-verification.md")
    log_redaction_plan = read_text(
        "docs/plans/2026-06-13-network-request-log-redaction.md"
    )
    ci_workflow = read_text(".github/workflows/check.yml")
    makefile = read_text("Makefile")
    readme = read_text("README.md")
    vision = read_text("VISION.md")
    security = read_text("SECURITY.md")
    changes = read_text("CHANGES.md")
    credential_plan = read_text(
        "docs/plans/2026-06-09-application-credential-initialization-guard.md"
    )
    location_manager_plan = read_text(
        "docs/plans/2026-06-09-main-activity-location-manager-guard.md"
    )
    permissions = manifest_permissions()

    require(
        '"https://garethpaul-app.appspot.com/api/airquality"' in network,
        "NetworkRequest must use the HTTPS air-quality endpoint",
        failures,
    )
    require(
        "URLEncoder.encode" in network and '"UTF-8"' in network,
        "NetworkRequest.buildUrl must URL-encode query values",
        failures,
    )
    require(
        "normalizeCoordinate(lat, \"lat\", -90.0, 90.0)" in network
        and "normalizeCoordinate(lng, \"lng\", -180.0, 180.0)" in network,
        "NetworkRequest.buildUrl must validate both coordinates before building a URL",
        failures,
    )
    require(
        "buildUrlFromParams(String... params)" in network
        and "params == null || params.length < 2" in network
        and "buildUrlFromParams(params)" in network,
        "NetworkRequest must validate AsyncTask parameters before building a request URL",
        failures,
    )
    require(
        "Double.isNaN" in network and "Double.isInfinite" in network,
        "NetworkRequest coordinate validation must reject non-finite values",
        failures,
    )
    require(
        "buildUrlTrimsLatitudeAndLongitude" in network_tests
        and "buildUrlRejectsMissingCoordinates" in network_tests
        and "buildUrlRejectsNonNumericAndOutOfRangeCoordinates" in network_tests
        and "Infinity" in network_tests,
        "NetworkRequestTest must cover trimming and invalid coordinate inputs",
        failures,
    )
    require(
        "buildUrlFromParamsUsesFirstLatitudeAndLongitude" in network_tests
        and "buildUrlFromParamsRejectsMissingAsyncTaskParameters" in network_tests
        and "assertInvalidParams((String[]) null)" in network_tests,
        "NetworkRequestTest must cover AsyncTask parameter validation",
        failures,
    )
    require(
        "catch (Throwable" not in network and "Log.w(TAG" in network,
        "NetworkRequest must not silently swallow broad background request failures",
        failures,
    )
    require(
        "request.get()" not in main_activity
        and "protected void onPostExecute(JSONObject response)" in main_activity
        and "state = readAirQualityState(response);" in main_activity,
        "MainActivity must update air quality from AsyncTask completion without blocking the UI thread",
        failures,
    )
    require(
        "private NetworkRequest airQualityRequest;" in main_activity
        and "airQualityRequest = new NetworkRequest()" in main_activity
        and "airQualityRequest.execute(" in main_activity,
        "MainActivity must retain the active air-quality request",
        failures,
    )
    callback_start = main_activity.find("protected void onPostExecute(JSONObject response)")
    callback = main_activity[callback_start:] if callback_start >= 0 else ""
    require(
        "if (airQualityRequest != this)" in callback
        and "airQualityRequest = null;" in callback
        and "isCancelled() || isFinishing() || isDestroyed()" in callback
        and callback.index("if (airQualityRequest != this)")
        < callback.index("state = readAirQualityState(response);")
        and callback.index("isCancelled() || isFinishing() || isDestroyed()")
        < callback.index("state = readAirQualityState(response);"),
        "MainActivity must ignore stale or teardown-time request callbacks",
        failures,
    )
    destroy_start = main_activity.find("protected void onDestroy()")
    destroy_method = main_activity[destroy_start:] if destroy_start >= 0 else ""
    require(
        "if (airQualityRequest != null)" in destroy_method
        and "airQualityRequest.cancel(true);" in destroy_method
        and "airQualityRequest = null;" in destroy_method
        and "super.onDestroy();" in destroy_method
        and destroy_method.index("airQualityRequest.cancel(true);")
        < destroy_method.index("super.onDestroy();"),
        "MainActivity must cancel and clear its request before destruction",
        failures,
    )
    require(
        "REQUEST_TIMEOUT_MILLIS" in network
        and "HttpConnectionParams.setConnectionTimeout(httpParams" in network
        and "HttpConnectionParams.setSoTimeout(httpParams, REQUEST_TIMEOUT_MILLIS)" in network
        and "new DefaultHttpClient(httpParams)" in network
        and "new DefaultHttpClient(p)" not in network,
        "NetworkRequest must apply request timeouts to the actual HTTP client",
        failures,
    )
    require(
        "private static final int RESPONSE_MAX_BYTES = 1024 * 1024;" in network,
        "NetworkRequest must cap backend responses at 1 MiB",
        failures,
    )
    require(
        "statusCode < 200 || statusCode >= 300" in network
        and 'throw new ClientProtocolException("Unexpected HTTP status")' in network,
        "NetworkRequest must reject non-2xx backend responses",
        failures,
    )
    require(
        "entity.getContentLength() > RESPONSE_MAX_BYTES" in network
        and "totalBytes > RESPONSE_MAX_BYTES" in network,
        "NetworkRequest must enforce declared and streamed response size limits",
        failures,
    )
    require(
        'return output.toString("UTF-8")' in network
        and "input.close()" in network
        and "httpclient.getConnectionManager().shutdown()" in network,
        "NetworkRequest must close response and connection resources after bounded UTF-8 decoding",
        failures,
    )
    require(
        "BasicResponseHandler" not in network and "ResponseHandler<String>" not in network,
        "NetworkRequest must not use an unbounded basic response handler",
        failures,
    )
    require(
        'DEFAULT_AIR_QUALITY_STATE = "Unknown"' in main_activity
        and "readAirQualityState(JSONObject response)" in main_activity
        and 'response.optString("air_quality", DEFAULT_AIR_QUALITY_STATE)'
        in main_activity,
        "MainActivity must default malformed or missing air-quality JSON safely",
        failures,
    )
    require(
        "GOOD_AIR_QUALITY_STATE.equals(state)" in main_activity
        and "state.equals(" not in main_activity,
        "MainActivity must compare air-quality state null-safely",
        failures,
    )
    require(
        "registerAccelerometerListener()" in main_activity
        and "private void registerAccelerometerListener()" in main_activity
        and "Sensor accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)" in main_activity
        and "if (sensorManager == null)" in main_activity
        and "if (accelerometer == null)" in main_activity
        and '"Accelerometer sensor unavailable"' in main_activity
        and "private void unregisterAccelerometerListener()" in main_activity
        and "if (sensorManager != null)" in main_activity,
        "MainActivity must guard accelerometer listener registration and cleanup",
        failures,
    )
    require(
        "if (event == null || event.sensor == null || event.values == null" in main_activity
        and "|| event.values.length < 3)" in main_activity
        and '"Ignoring malformed sensor event"' in main_activity
        and main_activity.index("if (event == null || event.sensor == null || event.values == null")
        < main_activity.index("displayAccelerometer(event)"),
        "MainActivity must guard malformed sensor events before rendering",
        failures,
    )
    require(
        "if (logo == null || text == null)" in main_activity
        and '"Air quality display views unavailable"' in main_activity
        and main_activity.index("if (logo == null || text == null)")
        < main_activity.index("logo.setBackgroundResource"),
        "MainActivity must guard display views before sensor-driven rendering",
        failures,
    )
    require(
        network.count("Log.w(") == 4
        and network.count('Log.w(TAG, "Air quality request failed");') == 2
        and network.count('Log.w(TAG, "Invalid air quality response JSON");') == 1
        and network.count('Log.w(TAG, "Invalid air quality request parameters");') == 1,
        "NetworkRequest must keep exactly four generic warning categories",
        failures,
    )
    require(
        not re.search(r'Log\.w\(TAG,\s*"[^"]+",\s*e\)', network)
        and "printStackTrace()" not in network
        and "Log.getStackTraceString" not in network
        and "e.getMessage()" not in network
        and "e.toString()" not in network,
        "NetworkRequest must not log throwable or exception-derived details",
        failures,
    )
    require(
        "if (locationManager == null)" in main_activity
        and '"Location manager unavailable"' in main_activity
        and main_activity.index("if (locationManager == null)")
        < main_activity.index(".isProviderEnabled(LocationManager.GPS_PROVIDER)"),
        "MainActivity must guard missing LocationManager before provider checks",
        failures,
    )
    require(
        login_activity.count("if (loginButton != null)") >= 2
        and login_activity.index("if (loginButton != null)")
        < login_activity.index("loginButton.setCallback")
        and 'Log.w("Login", "Twitter login button not found")' in login_activity,
        "LoginActivity must guard the Twitter login button before setting callbacks",
        failures,
    )
    result_method_start = login_activity.find("protected void onActivityResult")
    require(
        result_method_start >= 0,
        "LoginActivity must keep an onActivityResult override",
        failures,
    )
    result_method = login_activity[result_method_start:] if result_method_start >= 0 else ""
    require(
        "if (loginButton != null)" in result_method
        and "loginButton.onActivityResult(requestCode, resultCode, data)" in result_method
        and result_method.index("if (loginButton != null)")
        < result_method.index("loginButton.onActivityResult(requestCode, resultCode, data)"),
        "LoginActivity must guard loginButton before forwarding activity results",
        failures,
    )
    require(
        permissions.count("android.permission.ACCESS_FINE_LOCATION") == 1
        and permissions.count("android.permission.ACCESS_COARSE_LOCATION") == 1
        and permissions.count("android.permission.INTERNET") == 1,
        "AndroidManifest permissions must be present once each",
        failures,
    )
    require(
        ci_workflow == EXPECTED_CI_WORKFLOW,
        "GitHub Actions workflow must preserve the SDK-free matrix and exact hosted Android gate",
        failures,
    )
    require(
        "ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))" in makefile
        and "GRADLE ?= $(ROOT)/gradlew" in makefile
        and "CHECK_SCRIPT := $(ROOT)/scripts/check_airquality_android_contracts.py"
        in makefile
        and 'cd "$(ROOT)" && "$(GRADLE)"' in makefile,
        "Makefile must run SDK-free and Gradle checks from the repository root",
        failures,
    )
    require(
        'android:value=""' in manifest,
        "Fabric API key must remain empty in the checked-in manifest",
        failures,
    )
    require(
        'android:allowBackup="false"' in manifest
        and 'android:allowBackup="true"' not in manifest,
        "AndroidManifest must explicitly disable app-data backup",
        failures,
    )
    require(
        'TWITTER_KEY = ""' in application and 'TWITTER_SECRET = ""' in application,
        "Twitter credentials must remain empty in checked-in source",
        failures,
    )
    require(
        'private static final String TAG = "AirQualityApplication"' in application
        and "private boolean hasTwitterCredentials()" in application
        and "TWITTER_KEY.trim().length() > 0" in application
        and "TWITTER_SECRET.trim().length() > 0" in application
        and "if (!hasTwitterCredentials())" in application
        and 'Log.w(TAG, "Twitter credentials unavailable; skipping Fabric initialization")'
        in application
        and application.index("if (!hasTwitterCredentials())")
        < application.index("TwitterAuthConfig authConfig"),
        "AirQualityApplication must skip Fabric initialization when credentials are blank",
        failures,
    )
    require(
        "io.fabric.tools:gradle:1.+" not in app_build
        and "io.fabric.tools:gradle:1.14.4" in app_build
        and "project.hasProperty('fabricApiKey')" in app_build,
        "Fabric Gradle tooling must stay pinned and opt-in",
        failures,
    )
    require(
        "Status: Completed" in sensor_plan and "make check" in sensor_plan,
        "MainActivity sensor lifecycle plan must be completed and record make check",
        failures,
    )
    require(
        "Status: Completed" in credential_plan and "make check" in credential_plan,
        "AirQualityApplication credential guard plan must be completed and record make check",
        failures,
    )
    require(
        "Status: Completed" in location_manager_plan
        and "make check" in location_manager_plan,
        "MainActivity location manager guard plan must be completed and record make check",
        failures,
    )
    gitignore = read_text(".gitignore")
    for pattern in [".idea/", ".vscode/", "*.iml"]:
        require(
            pattern in gitignore,
            f".gitignore must keep {pattern} out of source control",
            failures,
        )
    tracked_editor_files = subprocess.run(
        ["git", "ls-files", "--", ".idea", ".vscode", "*.iml"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    ).stdout.splitlines()
    require(
        not tracked_editor_files,
        "IDE metadata must not be tracked: " + ", ".join(tracked_editor_files),
        failures,
    )
    require(
        "Status: Completed" in editor_metadata_plan and "make check" in editor_metadata_plan,
        "editor metadata ignore plan must be completed and record make check",
        failures,
    )
    require(
        "Status: Completed" in backup_plan and "make check" in backup_plan,
        "Android backup opt-out plan must be completed and record make check",
        failures,
    )
    require(
        "Status: Completed" in ci_plan and "make check" in ci_plan,
        "CI baseline plan must be completed and record make check",
        failures,
    )
    require(
        "Status: Completed" in response_limit_plan
        and "make check" in response_limit_plan,
        "network response size plan must be completed and record make check",
        failures,
    )
    require(
        "Status: Completed" in nonblocking_request_plan
        and "make check" in nonblocking_request_plan,
        "nonblocking MainActivity request plan must be completed and record make check",
        failures,
    )
    require(
        "Status: Completed" in request_lifecycle_plan
        and "make check" in request_lifecycle_plan,
        "MainActivity request lifecycle plan must be completed and record make check",
        failures,
    )
    require(
        "Status: Completed" in log_redaction_plan
        and "make check" in log_redaction_plan
        and "hostile mutations" in log_redaction_plan,
        "NetworkRequest log-redaction plan must record completed verification",
        failures,
    )
    require(
        read_text("gradle/wrapper/gradle-wrapper.properties")
        == EXPECTED_WRAPPER_PROPERTIES,
        "Gradle wrapper properties must retain the reviewed Gradle 2.2.1 URL and checksum",
        failures,
    )
    require(
        sha256("gradle/wrapper/gradle-wrapper.jar")
        == "7d3a4ac4de1c32b59bc6a4eb8ecb8e612ccd0cf1ae1e99f66902da64df296172",
        "Gradle wrapper JAR must match Gradle's published 8.14.5 wrapper checksum",
        failures,
    )
    require(
        sha256("gradlew")
        == "b187b4c52e749f5760afdd6fadc31b2a98ad35fb249bf0dff03b72650f320409"
        and sha256("gradlew.bat")
        == "94102713eb8fb22d032397924c0f38ab2da783ba60d07054339f1190a0c4e2cd",
        "Gradle wrapper launchers must match the reviewed generated scripts",
        failures,
    )
    require(
        "Gradle start up script for POSIX generated by Gradle." in read_text("gradlew")
        and "Gradle startup script for Windows" in read_text("gradlew.bat"),
        "Gradle wrapper launchers must retain generated provenance markers",
        failures,
    )
    require(
        "status: completed" in wrapper_plan
        and "fresh temporary Gradle user home" in wrapper_plan
        and "incorrect checksum was rejected" in wrapper_plan
        and "SDK-backed `make check` passed" in wrapper_plan
        and "external working directory" in wrapper_plan
        and "hostile mutations rejected" in wrapper_plan
        and "pull-request `Check` run `27440457696` passed" in wrapper_plan
        and "CodeQL run `27440455310` passed" in wrapper_plan
        and "6b5a6fbca8bdbd1455a5763bc468c91d3b28729b" in wrapper_plan,
        "Gradle wrapper plan must record completed local verification evidence",
        failures,
    )
    require(
        "distributionSha256Sum" in readme
        and "uncached build offline-reproducible" in readme
        and "wrapper JAR and Gradle distribution checksums" in security,
        "Repository docs must describe wrapper verification and its online boundary",
        failures,
    )
    for name, text in {
        "README.md": readme,
        "VISION.md": vision,
        "SECURITY.md": security,
        "CHANGES.md": changes,
    }.items():
        require(
            "GitHub Actions" in text,
            f"{name} must record the GitHub Actions CI baseline",
            failures,
        )
    require(
        "docs/plans/2026-06-10-ci-baseline.md" in readme,
        "README must link the CI baseline plan",
        failures,
    )
    for name, text in {
        "README.md": readme,
        "SECURITY.md": security,
        "CHANGES.md": changes,
    }.items():
        require(
            "generic networkrequest failure logs" in text.lower(),
            f"{name} must document generic NetworkRequest failure logs",
            failures,
        )

    if failures:
        print("AirQuality Android contract check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("AirQuality Android contract check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
