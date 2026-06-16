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


def java_method(source, signature):
    start = source.find(signature)
    if start < 0:
        return ""

    opening_brace = source.find("{", start)
    if opening_brace < 0:
        return ""

    depth = 0
    for index in range(opening_brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]

    return ""


def contains_in_order(source, *snippets):
    position = 0
    for snippet in snippets:
        position = source.find(snippet, position)
        if position < 0:
            return False
        position += len(snippet)
    return True


def manifest_permissions():
    manifest = ET.parse(ROOT / "app/src/main/AndroidManifest.xml").getroot()
    return [
        item.attrib.get(ANDROID_NS + "name")
        for item in manifest.findall("uses-permission")
    ]


def qualified_component_name(package_name, component_name):
    if component_name.startswith("."):
        return package_name + component_name
    if "." not in component_name:
        return package_name + "." + component_name
    return component_name


def merged_manifest_paths():
    intermediates = ROOT / "app/build/intermediates"
    if not intermediates.is_dir():
        return []

    manifests = []
    for path in intermediates.glob("**/AndroidManifest.xml"):
        path_parts = path.relative_to(intermediates).parts
        if "merged_manifests" in path_parts or (
            "manifests" in path_parts and "full" in path_parts
        ):
            manifests.append(path)
    return sorted(manifests)


def validate_activity_exports(path, failures):
    root = ET.parse(path).getroot()
    package_name = root.attrib.get("package", "")
    application = root.find("application")
    require(application is not None, f"{path} must declare an application", failures)
    if application is None:
        return

    activities = application.findall("activity")
    activities_by_name = {}
    for activity in activities:
        component_name = activity.attrib.get(ANDROID_NS + "name", "")
        qualified_name = qualified_component_name(package_name, component_name)
        activities_by_name.setdefault(qualified_name, []).append(activity)

    login_name = "twitterdev.airquality.LoginActivity"
    main_name = "twitterdev.airquality.MainActivity"
    login_activities = activities_by_name.get(login_name, [])
    main_activities = activities_by_name.get(main_name, [])
    require(
        len(login_activities) == 1,
        f"{path} must declare LoginActivity exactly once",
        failures,
    )
    require(
        len(main_activities) == 1,
        f"{path} must declare MainActivity exactly once",
        failures,
    )
    if len(login_activities) != 1 or len(main_activities) != 1:
        return

    login_activity = login_activities[0]
    main_activity = main_activities[0]
    require(
        login_activity.attrib.get(ANDROID_NS + "exported") == "true",
        f"{path} LoginActivity must be explicitly exported",
        failures,
    )
    require(
        main_activity.attrib.get(ANDROID_NS + "exported") == "false",
        f"{path} MainActivity must be explicitly non-exported",
        failures,
    )

    main_action = "android.intent.action.MAIN"
    launcher_category = "android.intent.category.LAUNCHER"
    launcher_owners = []
    login_launcher_filters = 0
    for activity in activities:
        component_name = activity.attrib.get(ANDROID_NS + "name", "")
        qualified_name = qualified_component_name(package_name, component_name)
        for intent_filter in activity.findall("intent-filter"):
            actions = {
                action.attrib.get(ANDROID_NS + "name")
                for action in intent_filter.findall("action")
            }
            categories = {
                category.attrib.get(ANDROID_NS + "name")
                for category in intent_filter.findall("category")
            }
            if main_action in actions and launcher_category in categories:
                launcher_owners.append(qualified_name)
                if activity is login_activity:
                    login_launcher_filters += 1

    require(
        launcher_owners == [login_name] and login_launcher_filters == 1,
        f"{path} LoginActivity must exclusively own one MAIN/LAUNCHER filter",
        failures,
    )


def main():
    failures = []

    network = read_text("app/src/main/java/twitterdev/airquality/NetworkRequest.java")
    main_activity = read_text("app/src/main/java/twitterdev/airquality/MainActivity.java")
    login_activity = read_text("app/src/main/java/twitterdev/airquality/LoginActivity.java")
    network_tests = read_text("app/src/test/java/twitterdev/airquality/NetworkRequestTest.java")
    main_activity_tests = read_text(
        "app/src/test/java/twitterdev/airquality/MainActivityTest.java"
    )
    root_build = read_text("build.gradle")
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
    location_log_redaction_plan = read_text(
        "docs/plans/2026-06-13-location-log-redaction.md"
    )
    location_gated_request_plan = read_text(
        "docs/plans/2026-06-13-location-gated-air-quality-request.md"
    )
    paused_request_plan = read_text(
        "docs/plans/2026-06-13-paused-air-quality-request-invalidation.md"
    )
    failed_request_retry_plan = read_text(
        "docs/plans/2026-06-13-failed-air-quality-request-resume-retry.md"
    )
    make_root_plan = read_text(
        "docs/plans/2026-06-14-make-root-override-protection.md"
    )
    strict_utf8_plan = read_text(
        "docs/plans/2026-06-14-strict-response-utf8-decoding.md"
    )
    redirect_plan = read_text(
        "docs/plans/2026-06-14-disable-air-quality-http-redirects.md"
    )
    media_type_plan = read_text(
        "docs/plans/2026-06-14-air-quality-json-media-type.md"
    )
    coordinate_serialization_plan = read_text(
        "docs/plans/2026-06-14-canonical-coordinate-serialization.md"
    )
    device_verification_plan = read_text(
        "docs/plans/2026-06-14-device-verification-checklist.md"
    )
    content_length_plan = read_text(
        "docs/plans/2026-06-14-strict-content-length-validation.md"
    )
    charset_plan = read_text(
        "docs/plans/2026-06-15-json-response-charset-validation.md"
    )
    quoted_comma_plan = read_text(
        "docs/plans/2026-06-15-quoted-content-type-commas.md"
    )
    duplicate_content_type_plan = read_text(
        "docs/plans/2026-06-15-duplicate-content-type-headers.md"
    )
    content_type_control_plan = read_text(
        "docs/plans/2026-06-15-content-type-control-character-rejection.md"
    )
    state_validation_plan = read_text(
        "docs/plans/2026-06-15-string-air-quality-state-validation.md"
    )
    state_whitespace_plan = read_text(
        "docs/plans/2026-06-15-canonical-air-quality-state-whitespace.md"
    )
    component_export_plan = read_text(
        "docs/plans/2026-06-16-explicit-android-component-exports.md"
    )
    zero_progress_read_plan = read_text(
        "docs/plans/2026-06-16-zero-progress-response-read.md"
    )
    device_verification = read_text("DEVICE_VERIFICATION.md")
    ci_workflow = read_text(".github/workflows/check.yml")
    makefile = read_text("Makefile")
    makefile_lines = set(makefile.splitlines())
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

    validate_activity_exports(ROOT / "app/src/main/AndroidManifest.xml", failures)
    for merged_manifest in merged_manifest_paths():
        validate_activity_exports(merged_manifest, failures)

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
        "return Double.toString(coordinate);" in network,
        "NetworkRequest must serialize validated coordinates as canonical decimal values",
        failures,
    )
    require(
        "buildUrlTrimsLatitudeAndLongitude" in network_tests
        and "buildUrlCanonicalizesJavaOnlyCoordinateSyntax" in network_tests
        and 'NetworkRequest.buildUrl("37.7d", "0x1.2p5")' in network_tests
        and "buildUrlRejectsMissingCoordinates" in network_tests
        and "buildUrlRejectsNonNumericAndOutOfRangeCoordinates" in network_tests
        and "Infinity" in network_tests,
        "NetworkRequestTest must cover trimming and invalid coordinate inputs",
        failures,
    )
    require(
        "Status: Completed" in coordinate_serialization_plan
        and "make check" in coordinate_serialization_plan
        and "mutations" in coordinate_serialization_plan.lower(),
        "canonical coordinate serialization plan must record completed verification",
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
    create_method = java_method(main_activity, "protected void onCreate(Bundle savedInstanceState)")
    resume_method = java_method(main_activity, "protected void onResume()")
    pause_method = java_method(main_activity, "protected void onPause()")
    cancel_request_method = java_method(
        main_activity, "private void cancelAirQualityRequest()"
    )
    location_request_method = java_method(
        main_activity,
        "private void requestAirQualityForLocation(Location currentLocation)",
    )
    location_changed_method = java_method(
        main_activity, "public void onLocationChanged(Location location)"
    )
    require(
        "getLocation();" not in create_method
        and "new NetworkRequest()" not in create_method
        and "airQualityRequest.execute(" not in create_method,
        "MainActivity onCreate must not start an air-quality request before location acquisition",
        failures,
    )
    require(
        "airQualityRequest == null" in resume_method
        and "location == null || restartAirQualityRequestOnResume" in resume_method
        and "restartAirQualityRequestOnResume = false;" in resume_method
        and "locationUpdatesActive = true;" in resume_method
        and "requestAirQualityForLocation(location != null ? location : getLocation());"
        in resume_method,
        "MainActivity must resume interrupted requests from retained or newly acquired location",
        failures,
    )
    require(
        "if (currentLocation == null || !locationUpdatesActive)" in location_request_method
        and "location = currentLocation;" in location_request_method
        and "latitude = currentLocation.getLatitude();" in location_request_method
        and "longitude = currentLocation.getLongitude();" in location_request_method
        and "stopLocationUpdates();" in location_request_method
        and "airQualityRequest.execute(" in location_request_method,
        "MainActivity must gate requests on an active non-null location and record its coordinates",
        failures,
    )
    require(
        location_request_method.count("airQualityRequest.execute(") == 1
        and contains_in_order(
            location_request_method,
            "location = currentLocation;",
            "latitude = currentLocation.getLatitude();",
            "longitude = currentLocation.getLongitude();",
            "stopLocationUpdates();",
            "airQualityRequest = new NetworkRequest()",
            "airQualityRequest.execute(",
        ),
        "MainActivity must record location and stop updates before creating or executing a request",
        failures,
    )
    require(
        "cancelAirQualityRequest();" in location_request_method
        and contains_in_order(
            location_request_method,
            "cancelAirQualityRequest();",
            "airQualityRequest = new NetworkRequest()",
        ),
        "MainActivity must cancel a superseded request before replacing it",
        failures,
    )
    require(
        "requestAirQualityForLocation(location);" in location_changed_method
        and "new NetworkRequest()" not in location_changed_method,
        "MainActivity location callbacks must delegate to the gated request helper",
        failures,
    )
    require(
        "restartAirQualityRequestOnResume = restartAirQualityRequestOnResume"
        in pause_method
        and "|| airQualityRequest != null;" in pause_method
        and "locationUpdatesActive = false;" in pause_method
        and "stopLocationUpdates();" in pause_method
        and "cancelAirQualityRequest();" in pause_method
        and "super.onPause();" in pause_method
        and contains_in_order(
            pause_method,
            "restartAirQualityRequestOnResume = restartAirQualityRequestOnResume",
            "|| airQualityRequest != null;",
            "stopLocationUpdates();",
            "cancelAirQualityRequest();",
            "super.onPause();",
        ),
        "MainActivity must preserve retry intent, stop location updates, and invalidate requests before pausing",
        failures,
    )
    require(
        "NetworkRequest request = airQualityRequest;" in cancel_request_method
        and "airQualityRequest = null;" in cancel_request_method
        and "if (request != null)" in cancel_request_method
        and "request.cancel(true);" in cancel_request_method
        and contains_in_order(
            cancel_request_method,
            "NetworkRequest request = airQualityRequest;",
            "airQualityRequest = null;",
            "request.cancel(true);",
        ),
        "MainActivity must clear request identity before cancellation",
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
    require(
        "restartAirQualityRequestOnResume = response == null;" in callback
        and callback.index("if (airQualityRequest != this)")
        < callback.index("restartAirQualityRequestOnResume = response == null;")
        and callback.index("isCancelled() || isFinishing() || isDestroyed()")
        < callback.index("restartAirQualityRequestOnResume = response == null;")
        < callback.index("state = readAirQualityState(response);"),
        "MainActivity must record failed request retry intent only for the current live callback",
        failures,
    )
    destroy_start = main_activity.find("protected void onDestroy()")
    destroy_method = main_activity[destroy_start:] if destroy_start >= 0 else ""
    require(
        "restartAirQualityRequestOnResume = false;" in destroy_method
        and "cancelAirQualityRequest();" in destroy_method
        and "locationUpdatesActive = false;" in destroy_method
        and "stopLocationUpdates();" in destroy_method
        and "super.onDestroy();" in destroy_method
        and contains_in_order(
            destroy_method, "stopLocationUpdates();", "super.onDestroy();"
        )
        and contains_in_order(
            destroy_method, "cancelAirQualityRequest();", "super.onDestroy();"
        ),
        "MainActivity must stop location updates and cancel its request before destruction",
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
        "HttpClientParams.setRedirecting(httpParams, false);" in network
        and contains_in_order(
            network,
            "HttpClientParams.setRedirecting(httpParams, false);",
            "new DefaultHttpClient(httpParams)",
        ),
        "NetworkRequest must disable redirects before constructing the HTTP client",
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
        "contentLength > RESPONSE_MAX_BYTES" in network
        and "totalBytes > RESPONSE_MAX_BYTES" in network,
        "NetworkRequest must enforce declared and streamed response size limits",
        failures,
    )
    require(
        "static long parseContentLength(String contentLength) throws IOException"
        in network
        and "character < '0' || character > '9'" in network
        and "parsedLength > (Long.MAX_VALUE - digit) / 10" in network,
        "NetworkRequest must parse Content-Length as overflow-safe ASCII digits",
        failures,
    )
    require(
        'response.getHeaders("Content-Length")' in network
        and "contentLengthHeaders.length > 1" in network
        and "contentLengthHeaders.length == 1" in network
        and "contentLength < -1" in network,
        "NetworkRequest must reject duplicate or invalid declared lengths",
        failures,
    )
    require(
        "static void requireJsonMediaType(String contentType) throws IOException"
        in network
        and '"application".equals(type)' in network
        and '"json".equals(subtype)' in network
        and 'subtype.endsWith("+json")' in network
        and "isMimeToken(type)" in network
        and "isMimeToken(subtype)" in network
        and "character >= 'a' && character <= 'z'" in network
        and "character >= '0' && character <= '9'" in network,
        "NetworkRequest must accept only unambiguous JSON application media types",
        failures,
    )
    require(
        "static void requireSingleJsonMediaType(String... contentTypes) throws IOException"
        in network
        and "contentTypes == null || contentTypes.length != 1" in network
        and "requireJsonMediaType(contentTypes[0])" in network,
        "NetworkRequest must reject missing or duplicate Content-Type headers",
        failures,
    )
    require(
        "requireUtf8MediaTypeParameters(contentType, parameterStart)" in network
        and "boolean charsetSeen = false;" in network
        and '"charset".equals(name)' in network
        and '"utf-8".equals(normalizedValue)' in network
        and "readQuotedParameter" in network
        and "skipHttpWhitespace" in network,
        "NetworkRequest must require unambiguous UTF-8 charset metadata",
        failures,
    )
    require(
        "private static String trimHttpWhitespace(String value)" in network
        and "mediaType = trimHttpWhitespace(mediaType)" in network
        and "String name = trimHttpWhitespace(contentType.substring(nameStart, index))"
        in network
        and "String tokenValue = trimHttpWhitespace(" in network
        and "value.charAt(end - 1) == ' '" in network
        and "value.charAt(end - 1) == '\\t'" in network,
        "NetworkRequest must trim only HTTP space and tab outside quoted values",
        failures,
    )
    require(
        contains_in_order(
            network,
            "HttpEntity entity = response.getEntity();",
            'response.getHeaders("Content-Type")',
            "contentTypes[index] = contentTypeHeaders[index].getValue();",
            "requireSingleJsonMediaType(contentTypes);",
            'response.getHeaders("Content-Length")',
            "parseContentLength(contentLengthHeaders[0].getValue())",
            "entity.getContent();",
        ),
        "NetworkRequest must validate media type and length before body access",
        failures,
    )
    require(
        "requireSingleJsonMediaTypeRejectsAmbiguousHeaders" in network_tests
        and 'requireSingleJsonMediaType("application/json")' in network_tests
        and 'assertInvalidResponseMediaType("application/json", "application/json")'
        in network_tests
        and 'assertInvalidResponseMediaType("application/json", "text/html")'
        in network_tests,
        "NetworkRequestTest must cover missing and duplicate Content-Type headers",
        failures,
    )
    require(
        "parseContentLengthAcceptsAsciiDecimalValues" in network_tests
        and "parseContentLengthRejectsMalformedAndOverflowingValues" in network_tests
        and "assertInvalidContentLength(null)" in network_tests
        and 'assertInvalidContentLength("1_0")' in network_tests
        and 'assertInvalidContentLength("1, 2")' in network_tests
        and 'assertInvalidContentLength("9223372036854775808")' in network_tests,
        "NetworkRequestTest must cover strict Content-Length parsing",
        failures,
    )
    require(
        "requireJsonMediaTypeAcceptsJsonApplicationTypes" in network_tests
        and "requireJsonMediaTypeRejectsMissingAmbiguousAndNonJsonTypes"
        in network_tests
        and 'assertInvalidMediaType("application/json, text/html")'
        in network_tests
        and 'assertInvalidMediaType("application/caf\\u00e9+json")'
        in network_tests
        and 'assertInvalidMediaType("text/html")' in network_tests,
        "NetworkRequest JSON media type behavior must retain focused unit coverage",
        failures,
    )
    require(
        "requireJsonMediaTypeRejectsControlsOutsideQuotedValues" in network_tests
        and 'assertInvalidMediaType("\\rapplication/json")' in network_tests
        and 'assertInvalidMediaType("application/json\\n")' in network_tests
        and 'assertInvalidMediaType("application/json;\\u000bcharset=UTF-8")'
        in network_tests
        and 'assertInvalidMediaType("application/json; charset=\\rUTF-8")'
        in network_tests
        and '" \\tapplication/json\\t ;\\tcharset\\t=\\tUTF-8\\t"'
        in network_tests,
        "NetworkRequest media type tests must reject controls and preserve HTTP OWS",
        failures,
    )
    require(
        "contentType.indexOf(',')" not in network
        and 'profile=\\"https://example.test/schema,a=b\\"' in network_tests
        and 'assertInvalidMediaType("application/json, text/html")'
        in network_tests,
        "Content-Type comma handling must distinguish quoted data from combined values",
        failures,
    )
    require(
        'NetworkRequest.requireJsonMediaType("application/json; charset=\\"utf-8\\"")'
        in network_tests
        and 'profile=\\"https://example.test/schema;a=b\\"' in network_tests
        and 'charset = \\"UTF-8\\"' in network_tests
        and 'assertInvalidMediaType("application/json; charset=ISO-8859-1")'
        in network_tests
        and 'assertInvalidMediaType("application/json; charset=UTF-8; charset=UTF-8")'
        in network_tests
        and 'assertInvalidMediaType("application/json; charset=UTF-8; charset=ISO-8859-1")'
        in network_tests
        and 'assertInvalidMediaType("application/json; profile=\\"unterminated")'
        in network_tests,
        "NetworkRequestTest must cover UTF-8 charset and malformed parameter handling",
        failures,
    )
    require(
        "static String decodeUtf8(byte[] bytes) throws IOException" in network
        and "StandardCharsets.UTF_8.newDecoder()" in network
        and ".onMalformedInput(CodingErrorAction.REPORT)" in network
        and ".onUnmappableCharacter(CodingErrorAction.REPORT)" in network
        and ".decode(ByteBuffer.wrap(bytes))" in network
        and "return decodeUtf8(output.toByteArray());" in network
        and 'output.toString("UTF-8")' not in network,
        "NetworkRequest must reject malformed UTF-8 after bounding response bytes",
        failures,
    )
    require(
        "static String readBoundedUtf8(InputStream input) throws IOException" in network
        and "while ((bytesRead = input.read(buffer)) != -1)" in network
        and "if (bytesRead == 0)" in network
        and 'throw new IOException("Air quality response read made no progress")'
        in network
        and "if (totalBytes > RESPONSE_MAX_BYTES)" in network
        and "return decodeUtf8(output.toByteArray());" in network
        and "return readBoundedUtf8(input);" in network,
        "NetworkRequest must bound response reads and reject zero progress",
        failures,
    )
    require(
        "readBoundedUtf8AccumulatesFragmentedReads" in network_tests
        and "readBoundedUtf8RejectsZeroProgress" in network_tests
        and "readBoundedUtf8AcceptsExactResponseLimit" in network_tests
        and "readBoundedUtf8RejectsResponseOverLimit" in network_tests
        and "new ZeroProgressInputStream()" in network_tests,
        "NetworkRequestTest must cover fragmented, zero-progress, and bounded reads",
        failures,
    )
    require(
        "decodeUtf8PreservesValidJson" in network_tests
        and "decodeUtf8RejectsMalformedInput" in network_tests,
        "NetworkRequest strict UTF-8 behavior must retain focused unit coverage",
        failures,
    )
    require(
        "input.close()" in network
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
        and 'Object rawAirQuality = response.opt("air_quality");' in main_activity
        and "if (!(rawAirQuality instanceof String))" in main_activity
        and "String airQuality = ((String) rawAirQuality).trim();" in main_activity,
        "MainActivity must default malformed or missing air-quality JSON safely",
        failures,
    )
    for contract in (
        "readAirQualityStateDefaultsMissingNullBlankAndNonStringValues",
        "responseWith(JSONObject.NULL)",
        "responseWith(true)",
        "responseWith(42)",
        'new JSONObject().put("nested", "value")',
        'new JSONArray().put("Good")',
    ):
        require(
            contract in main_activity_tests,
            f"MainActivity string-state tests must keep contract: {contract}",
            failures,
        )
    for contract in (
        "readAirQualityStateTrimsNonblankStrings",
        'responseWith("  Good \\t")',
        'responseWith("\\nModerate ")',
    ):
        require(
            contract in main_activity_tests,
            f"MainActivity state-whitespace tests must keep contract: {contract}",
            failures,
        )
    require(
        "repositories {\n        mavenCentral()\n        jcenter()\n    }" in root_build
        and "testCompile 'org.json:json:20260522'" in app_build,
        "Android JVM tests must use the pinned Java 8 JSON implementation from Maven Central",
        failures,
    )
    require(
        "org.json:json:" not in "\n".join(
            line for line in app_build.splitlines() if "testCompile" not in line
        ),
        "The real JSON implementation must remain test-only",
        failures,
    )
    require(
        "Android JVM tests use pinned `org.json:json:20260522` semantics" in readme
        and "test-only JSON implementation" in changes,
        "Maintained guidance must document the real test-only JSON implementation",
        failures,
    )
    for contract in (
        "Hosted Android Follow-Up",
        "org.json:json:20260522",
        "Java 8",
        "test-only dependency",
        "new exact-head hosted result",
        "Hosted Correction Completed",
        "fresh Gradle user home",
        "Eight hostile mutations",
    ):
        require(
            contract in state_validation_plan,
            f"String state hosted correction plan must keep contract: {contract}",
            failures,
        )
    for name, text in {
        "README.md": readme,
        "SECURITY.md": security,
        "VISION.md": vision,
        "CHANGES.md": changes,
    }.items():
        require(
            "MainActivity accepts air_quality only when its JSON value is a nonblank string."
            in text,
            f"{name} must document strict air-quality state typing",
            failures,
        )
    for contract in (
        "status: completed",
        "readAirQualityStateDefaultsMissingNullBlankAndNonStringValues",
        "make check",
        "hostile mutations",
    ):
        require(
            contract in state_validation_plan,
            f"String state validation plan must keep contract: {contract}",
            failures,
        )
    for name, text in {
        "README.md": readme,
        "SECURITY.md": security,
        "VISION.md": vision,
        "CHANGES.md": changes,
    }.items():
        require(
            "MainActivity trims surrounding whitespace from nonblank air_quality strings."
            in text,
            f"{name} must document canonical air-quality state whitespace",
            failures,
        )
    for contract in (
        "status: completed",
        "readAirQualityStateTrimsNonblankStrings",
        "make check",
        "Six isolated hostile mutations",
        "credential-shaped addition audits",
    ):
        require(
            contract in state_whitespace_plan,
            f"State whitespace plan must keep contract: {contract}",
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
        main_activity.count('Log.w(TAG, "Unable to read device location");') == 1,
        "MainActivity must keep one generic location failure warning",
        failures,
    )
    require(
        not re.search(r'Log\.w\(TAG,\s*"Unable to read device location",', main_activity)
        and "printStackTrace()" not in main_activity
        and "Log.getStackTraceString" not in main_activity
        and "e.getMessage()" not in main_activity
        and "e.toString()" not in main_activity,
        "MainActivity must not log throwable or exception-derived location details",
        failures,
    )
    require(
        "Generic location acquisition failure logs" in readme
        and "Generic location acquisition failure logs" in security
        and "location log boundary" in changes,
        "Repository guidance must document the generic location log boundary",
        failures,
    )
    require(
        all(
            "Response charset metadata must be absent or unambiguous UTF-8" in text
            for text in (readme, security, vision, changes)
        ),
        "Repository guidance must document response charset consistency",
        failures,
    )
    require(
        all(
            "Quoted Content-Type parameter values may contain commas" in text
            for text in (readme, security, vision, changes)
        ),
        "Repository guidance must document quote-aware Content-Type comma handling",
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
        "new Intent(getApplicationContext(), MainActivity.class)" in login_activity,
        "LoginActivity must keep an explicit in-app transition to MainActivity",
        failures,
    )
    component_export_guidance = (
        "LoginActivity is the only exported launcher; MainActivity is explicitly "
        "non-exported and reached with an explicit in-app intent."
    )
    for document_name, document in (
        ("README.md", readme),
        ("SECURITY.md", security),
        ("VISION.md", vision),
        ("CHANGES.md", changes),
    ):
        require(
            component_export_guidance in document,
            f"{document_name} must document explicit activity export ownership",
            failures,
        )
    for contract in (
        "Status: Completed",
        "Repository and external-directory `make check` passed",
        "hostile mutations were rejected",
        "source and generated merged manifests",
        "No emulator or physical-device scenario was executed",
    ):
        require(
            contract in component_export_plan,
            f"Explicit component export plan must keep contract: {contract}",
            failures,
        )
    zero_progress_guidance = (
        "Backend response reads fail when a stream reports zero progress instead of "
        "spinning indefinitely."
    )
    for document_name, document in (
        ("README.md", readme),
        ("SECURITY.md", security),
        ("VISION.md", vision),
        ("CHANGES.md", changes),
    ):
        require(
            zero_progress_guidance in document,
            f"{document_name} must document zero-progress response read rejection",
            failures,
        )
    for contract in (
        "Status: Completed",
        "readBoundedUtf8RejectsZeroProgress",
        "repository and external-directory `make check` passed",
        "hostile mutations were rejected",
        "generated-artifact and credential scans passed",
    ):
        require(
            contract in zero_progress_read_plan,
            f"Zero-progress response read plan must keep contract: {contract}",
            failures,
        )
    require(
        ci_workflow == EXPECTED_CI_WORKFLOW,
        "GitHub Actions workflow must preserve the SDK-free matrix and exact hosted Android gate",
        failures,
    )
    require(
        "override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))"
        in makefile_lines
        and "PYTHON ?= python3" in makefile_lines
        and "GRADLE ?= $(ROOT)/gradlew" in makefile_lines
        and "CHECK_SCRIPT := $(ROOT)/scripts/check_airquality_android_contracts.py"
        in makefile_lines
        and 'cd "$(ROOT)" && "$(GRADLE)"' in makefile,
        "Makefile must run SDK-free and Gradle checks from the repository root",
        failures,
    )
    require(
        '"$(GRADLE)" lint test assembleDebug --no-daemon && \\' in makefile
        and '$(PYTHON) "$(CHECK_SCRIPT)"; \\' in makefile,
        "Makefile must preserve Gradle failure status before checking merged manifests",
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
        "Status: Completed" in location_log_redaction_plan
        and "make check" in location_log_redaction_plan
        and "hostile mutations" in location_log_redaction_plan,
        "MainActivity location log-redaction plan must record completed verification",
        failures,
    )
    require(
        "Status: Completed" in location_gated_request_plan
        and "make check" in location_gated_request_plan
        and "hostile mutations" in location_gated_request_plan,
        "location-gated request plan must record completed verification",
        failures,
    )
    require(
        "Status: Completed" in paused_request_plan
        and "make check" in paused_request_plan
        and "hostile mutations" in paused_request_plan,
        "paused request invalidation plan must record completed verification",
        failures,
    )
    require(
        "Status: Completed" in failed_request_retry_plan
        and "make check" in failed_request_retry_plan
        and "hostile mutations" in failed_request_retry_plan.lower(),
        "failed request resume retry plan must record completed verification",
        failures,
    )
    require(
        "Status: Completed" in make_root_plan
        and "make check" in make_root_plan
        and "mutations" in make_root_plan.lower(),
        "Make root protection plan must record completed verification",
        failures,
    )
    require(
        "Status: Completed" in strict_utf8_plan
        and "make check" in strict_utf8_plan
        and "mutations" in strict_utf8_plan.lower(),
        "strict response UTF-8 plan must record completed verification",
        failures,
    )
    require(
        "Status: Completed" in redirect_plan
        and "make check" in redirect_plan
        and "mutations" in redirect_plan.lower(),
        "HTTP redirect rejection plan must record completed verification",
        failures,
    )
    require(
        "rejects automatic redirects" in readme
        and "reject automatic redirects" in security
        and "Reject automatic backend redirects" in vision
        and "Disabled automatic backend redirects" in changes,
        "HTTP redirect rejection must remain documented",
        failures,
    )
    require(
        "rejects malformed UTF-8" in readme
        and "reject malformed UTF-8" in security
        and "Reject malformed UTF-8" in vision
        and "Rejected malformed UTF-8 backend responses" in changes,
        "strict backend response UTF-8 decoding must remain documented",
        failures,
    )
    require(
        "Status: Completed" in media_type_plan
        and "make check" in media_type_plan
        and "mutations" in media_type_plan.lower(),
        "JSON response media type plan must record completed verification",
        failures,
    )
    require(
        "Status: Completed" in content_length_plan
        and "make check" in content_length_plan
        and "mutations" in content_length_plan.lower(),
        "strict Content-Length plan must record completed verification",
        failures,
    )
    require(
        "status: completed" in charset_plan
        and "make check" in charset_plan
        and "external working directory" in charset_plan
        and "hostile mutations" in charset_plan
        and "secret and generated-artifact scan" in charset_plan,
        "JSON response charset plan must record completed verification",
        failures,
    )
    require(
        "status: completed" in quoted_comma_plan
        and "make check" in quoted_comma_plan
        and "external working directory" in quoted_comma_plan
        and "hostile mutations" in quoted_comma_plan
        and "secret and generated-artifact scan" in quoted_comma_plan,
        "quoted Content-Type comma plan must record completed verification",
        failures,
    )
    for contract in (
        "status: completed",
        "requireSingleJsonMediaTypeRejectsAmbiguousHeaders",
        "make check",
        "isolated hostile mutations",
        "secret and generated-artifact scan",
    ):
        require(
            contract in duplicate_content_type_plan,
            f"Duplicate Content-Type plan must keep contract: {contract}",
            failures,
        )
    duplicate_content_type_guidance = (
        "Backend responses must contain exactly one Content-Type header before body access."
    )
    for document_name, document in (
        ("README.md", readme),
        ("SECURITY.md", security),
        ("VISION.md", vision),
        ("CHANGES.md", changes),
    ):
        require(
            duplicate_content_type_guidance in document,
            f"{document_name} must document duplicate Content-Type rejection",
            failures,
        )

    content_type_control_guidance = (
        "Response Content-Type parsing accepts only space and tab as optional HTTP "
        "whitespace; CR, LF, and other controls fail before body access."
    )
    for document_name, document in (
        ("README.md", readme),
        ("SECURITY.md", security),
        ("VISION.md", vision),
        ("CHANGES.md", changes),
    ):
        require(
            content_type_control_guidance in document,
            f"{document_name} must document Content-Type control rejection",
            failures,
        )

    for contract in (
        "Status: Completed",
        "requireJsonMediaTypeRejectsControlsOutsideQuotedValues",
        "repository and external-directory `make check` passed",
        "hostile mutations were rejected",
    ):
        require(
            contract in content_type_control_plan,
            f"Content-Type control-character plan must keep contract: {contract}",
            failures,
        )
    require(
        "strict Content-Length" in readme
        and "strict Content-Length" in security
        and "Strict backend Content-Length" in vision
        and "Validated strict backend Content-Length" in changes,
        "strict Content-Length validation must remain documented",
        failures,
    )
    require(
        "requires JSON response media types" in readme
        and "require JSON application media types" in security
        and "Require JSON application media types" in vision
        and "Required JSON application media types" in changes,
        "JSON response media type validation must remain documented",
        failures,
    )
    require(
        "canonical decimal coordinate values" in readme
        and "canonical decimal coordinates" in security
        and "canonical decimal coordinates" in vision
        and "Canonicalized validated coordinates" in changes,
        "canonical coordinate serialization must remain documented",
        failures,
    )
    require(
        "Failed air-quality requests retain one resume-time retry" in readme
        and "pause must not discard it" in security
        and "Preserve failed-request retry intent" in vision
        and "Preserved failed air-quality request retry intent" in changes,
        "failed request resume retry must remain documented across project guidance",
        failures,
    )
    require(
        "background request invalidation" in readme
        and "before pause" in security
        and "Invalidate in-flight backend work" in vision
        and "Invalidated and cancelled in-flight air-quality requests on pause"
        in changes,
        "paused request invalidation must remain documented across project guidance",
        failures,
    )
    require(
        "waits for a non-null location" in readme
        and "stops location updates" in security
        and "location-gated backend requests" in vision
        and "location-gated" in changes,
        "project docs must describe the location-gated request lifecycle",
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

    for contract in (
        "commit SHA and pull request",
        "./gradlew lint test assembleDebug --no-daemon",
        "Location permission denied",
        "Pause during request",
        "Rotate during backend request",
        "Process recreation",
        "malformed UTF-8 and malformed JSON",
        "Do not convert `not run` into a passing result.",
        "latitude, longitude, request URLs",
        "currently records the matrix as unexecuted",
    ):
        require(
            contract in device_verification,
            f"Device verification checklist must keep contract: {contract}",
            failures,
        )
    require(
        "DEVICE_VERIFICATION.md" in readme
        and "unexecuted scenarios explicit" in readme
        and "device verification matrix" in vision.lower()
        and "explicit `not run` results" in changes,
        "Repository guidance must document the unexecuted device matrix",
        failures,
    )
    require(
        "Status: Completed" in device_verification_plan
        and "make check" in device_verification_plan
        and "hostile mutations" in device_verification_plan
        and "No emulator or physical-device scenario was executed" in device_verification_plan,
        "Device verification plan must record completed portable evidence and runtime non-claims",
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
