#!/usr/bin/env python3
"""Static contracts for the legacy AirQuality Android project."""

from pathlib import Path
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
    network_tests = read_text("app/src/test/java/twitterdev/airquality/NetworkRequestTest.java")
    app_build = read_text("app/build.gradle")
    application = read_text("app/src/main/java/twitterdev/airquality/AirQualityApplication.java")
    manifest = read_text("app/src/main/AndroidManifest.xml")
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
        permissions.count("android.permission.ACCESS_FINE_LOCATION") == 1
        and permissions.count("android.permission.ACCESS_COARSE_LOCATION") == 1
        and permissions.count("android.permission.INTERNET") == 1,
        "AndroidManifest permissions must be present once each",
        failures,
    )
    require(
        'android:value=""' in manifest,
        "Fabric API key must remain empty in the checked-in manifest",
        failures,
    )
    require(
        'TWITTER_KEY = ""' in application and 'TWITTER_SECRET = ""' in application,
        "Twitter credentials must remain empty in checked-in source",
        failures,
    )
    require(
        "io.fabric.tools:gradle:1.+" not in app_build
        and "io.fabric.tools:gradle:1.14.4" in app_build
        and "project.hasProperty('fabricApiKey')" in app_build,
        "Fabric Gradle tooling must stay pinned and opt-in",
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
