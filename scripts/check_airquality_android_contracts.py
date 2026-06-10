#!/usr/bin/env python3
"""Static contracts for the legacy AirQuality Android project."""

from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def workflow_section(source, heading):
    lines = source.splitlines()
    start = next(
        (index for index, line in enumerate(lines) if line == f"{heading}:"),
        None,
    )
    if start is None:
        return ""
    end = next(
        (
            index
            for index, line in enumerate(lines[start + 1 :], start + 1)
            if line and not line.startswith(" ") and not line.startswith("#")
        ),
        len(lines),
    )
    return "\n".join(lines[start + 1 : end])


def workflow_action_refs(source):
    return re.findall(r"^\s*-?\s*uses:\s+([^\s#]+)", source, re.MULTILINE)


def workflow_has_line(source, pattern):
    return re.search(pattern, source, re.MULTILINE) is not None


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
    ci_workflow = read_text(".github/workflows/check.yml")
    makefile = read_text("Makefile")
    credential_plan = read_text(
        "docs/plans/2026-06-09-application-credential-initialization-guard.md"
    )
    location_manager_plan = read_text(
        "docs/plans/2026-06-09-main-activity-location-manager-guard.md"
    )
    permissions = manifest_permissions()
    workflow_sources = {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for pattern in ("*.yml", "*.yaml")
        for path in (ROOT / ".github/workflows").glob(pattern)
    }
    tracked_paths = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()

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
        "printStackTrace()" not in main_activity
        and 'Log.w(TAG, "Air quality request failed"' in network
        and 'Log.w(TAG, "Invalid air quality response JSON"' in network,
        "NetworkRequest must log request failures without raw stack traces",
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
    trigger_section = workflow_section(ci_workflow, "on")
    permissions_section = workflow_section(ci_workflow, "permissions")
    jobs_section = workflow_section(ci_workflow, "jobs")
    action_refs = workflow_action_refs(ci_workflow)
    trigger_names = re.findall(r"^  ([A-Za-z0-9_-]+):", trigger_section, re.MULTILINE)
    job_names = re.findall(r"^  ([A-Za-z0-9_-]+):$", jobs_section, re.MULTILINE)
    require(
        all(
            re.fullmatch(r"[^@\s]+@[0-9a-f]{40}", action_ref)
            for source in workflow_sources.values()
            for action_ref in workflow_action_refs(source)
        ),
        "Every hosted workflow action must use an immutable revision",
        failures,
    )
    require(
        trigger_names == ["pull_request", "push", "workflow_dispatch"]
        and "      - master" in trigger_section,
        "GitHub Actions must use only pull request, master push, and manual triggers",
        failures,
    )
    require(
        permissions_section.strip() == "contents: read",
        "GitHub Actions must use read-only repository permissions",
        failures,
    )
    require(
        job_names == ["check"]
        and action_refs
        == [
            "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
            "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        ],
        "GitHub Actions must use only the canonical check job and immutable checkout and setup-python actions",
        failures,
    )
    require(
        "runs-on: ubuntu-24.04" in jobs_section
        and 'python-version: ["3.10", "3.12", "3.14"]' in jobs_section
        and "python-version: ${{ matrix.python-version }}" in jobs_section,
        "GitHub Actions must use Ubuntu 24.04 and verify the supported Python matrix",
        failures,
    )
    require(
        "workflow_dispatch:" in trigger_section
        and workflow_has_line(jobs_section, r"^\s+timeout-minutes: 5$")
        and workflow_has_line(jobs_section, r"^\s+persist-credentials: false$")
        and workflow_has_line(jobs_section, r"^\s+run: make check$")
        and workflow_has_line(jobs_section, r'^\s+SKIP_GRADLE: "1"$')
        and "concurrency:" in ci_workflow
        and "cancel-in-progress: true" in ci_workflow
        and not workflow_has_line(jobs_section, r"^\s{4,}permissions:")
        and "write-all" not in ci_workflow
        and "pull_request_target" not in ci_workflow,
        "GitHub Actions must run the bounded SDK-free make check baseline without persisted credentials",
        failures,
    )
    require(
        "ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))" in makefile
        and "GRADLE ?= $(ROOT)/gradlew" in makefile
        and "CHECK_SCRIPT := $(ROOT)/scripts/check_airquality_android_contracts.py"
        in makefile
        and 'if [ "$$SKIP_GRADLE" = "1" ]' in makefile
        and makefile.index('if [ "$$SKIP_GRADLE" = "1" ]')
        < makefile.index('[ -f "$(ROOT)/local.properties" ]')
        and 'cd "$(ROOT)" && "$(GRADLE)"' in makefile,
        "Makefile must run SDK-free and Gradle checks from the repository root",
        failures,
    )
    require(
        "local.properties" not in tracked_paths,
        "local.properties must never be tracked",
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

    if failures:
        print("AirQuality Android contract check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("AirQuality Android contract check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
