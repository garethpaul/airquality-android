#!/usr/bin/env python3
"""Static contracts for the legacy AirQuality Android project."""

from pathlib import Path
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
    ci_workflow = read_text(".github/workflows/check.yml")
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
        "REQUEST_TIMEOUT_MILLIS" in network
        and "HttpConnectionParams.setConnectionTimeout(httpParams" in network
        and "HttpConnectionParams.setSoTimeout(httpParams, REQUEST_TIMEOUT_MILLIS)" in network
        and "new DefaultHttpClient(httpParams)" in network
        and "new DefaultHttpClient(p)" not in network,
        "NetworkRequest must apply request timeouts to the actual HTTP client",
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
        and "Thread.currentThread().interrupt()" in main_activity
        and 'Log.w(TAG, "Unable to load air quality"' in main_activity,
        "MainActivity must log request failures without raw stack traces",
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
        "permissions:\n  contents: read" in ci_workflow
        and "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10" in ci_workflow
        and "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405" in ci_workflow
        and 'python-version: ["3.10", "3.12", "3.14"]' in ci_workflow
        and "workflow_dispatch:" in ci_workflow
        and "timeout-minutes: 5" in ci_workflow
        and 'ANDROID_HOME: ""' in ci_workflow
        and 'ANDROID_SDK_ROOT: ""' in ci_workflow
        and "run: make check" in ci_workflow,
        "GitHub Actions workflow must run the pinned, read-only SDK-free Python matrix",
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

    if failures:
        print("AirQuality Android contract check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("AirQuality Android contract check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
