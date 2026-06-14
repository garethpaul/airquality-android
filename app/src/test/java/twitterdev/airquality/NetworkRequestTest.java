package twitterdev.airquality;

import org.junit.Test;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

public class NetworkRequestTest {
    @Test
    public void buildUrlIncludesLatitudeAndLongitude() {
        assertEquals(
                "https://garethpaul-app.appspot.com/api/airquality?lat=37.7&lng=-122.4",
                NetworkRequest.buildUrl("37.7", "-122.4"));
    }

    @Test
    public void buildUrlTrimsLatitudeAndLongitude() {
        assertEquals(
                "https://garethpaul-app.appspot.com/api/airquality?lat=37.7&lng=-122.4",
                NetworkRequest.buildUrl(" 37.7 ", " -122.4 "));
    }

    @Test
    public void buildUrlCanonicalizesJavaOnlyCoordinateSyntax() {
        assertEquals(
                "https://garethpaul-app.appspot.com/api/airquality?lat=37.7&lng=36.0",
                NetworkRequest.buildUrl("37.7d", "0x1.2p5"));
    }

    @Test
    public void buildUrlFromParamsUsesFirstLatitudeAndLongitude() {
        assertEquals(
                "https://garethpaul-app.appspot.com/api/airquality?lat=37.7&lng=-122.4",
                NetworkRequest.buildUrlFromParams("37.7", "-122.4", "ignored"));
    }

    @Test
    public void buildUrlFromParamsRejectsMissingAsyncTaskParameters() {
        assertInvalidParams((String[]) null);
        assertInvalidParams();
        assertInvalidParams("37.7");
    }

    @Test
    public void buildUrlRejectsMissingCoordinates() {
        assertInvalidCoordinate(null, "-122.4");
        assertInvalidCoordinate("", "-122.4");
        assertInvalidCoordinate("37.7", " ");
    }

    @Test
    public void buildUrlRejectsNonNumericAndOutOfRangeCoordinates() {
        assertInvalidCoordinate("not-a-number", "-122.4");
        assertInvalidCoordinate("NaN", "-122.4");
        assertInvalidCoordinate("37.7", "Infinity");
        assertInvalidCoordinate("91", "-122.4");
        assertInvalidCoordinate("37.7", "-181");
    }

    @Test
    public void decodeUtf8PreservesValidJson() throws IOException {
        assertEquals(
                "{\"results\":[]}",
                NetworkRequest.decodeUtf8(
                        "{\"results\":[]}".getBytes(StandardCharsets.UTF_8)));
    }

    @Test
    public void decodeUtf8RejectsMalformedInput() {
        try {
            NetworkRequest.decodeUtf8(new byte[] {(byte) 0xC3, 0x28});
            fail("Expected malformed UTF-8 to be rejected");
        } catch (IOException expected) {
            // Expected path.
        }
    }

    @Test
    public void requireJsonMediaTypeAcceptsJsonApplicationTypes() throws IOException {
        NetworkRequest.requireJsonMediaType("Application/JSON; charset=UTF-8");
        NetworkRequest.requireJsonMediaType("application/problem+json");
        NetworkRequest.requireJsonMediaType(" application/vnd.airquality.v1+json ");
    }

    @Test
    public void requireJsonMediaTypeRejectsMissingAmbiguousAndNonJsonTypes() {
        assertInvalidMediaType(null);
        assertInvalidMediaType("");
        assertInvalidMediaType("application/json, text/html");
        assertInvalidMediaType("application/+json");
        assertInvalidMediaType("application/vnd api+json");
        assertInvalidMediaType("application/caf\u00e9+json");
        assertInvalidMediaType("text/json");
        assertInvalidMediaType("text/html");
    }

    @Test
    public void parseContentLengthAcceptsAsciiDecimalValues() throws IOException {
        assertEquals(0L, NetworkRequest.parseContentLength("0"));
        assertEquals(1048576L, NetworkRequest.parseContentLength("1048576"));
        assertEquals(Long.MAX_VALUE, NetworkRequest.parseContentLength("9223372036854775807"));
    }

    @Test
    public void parseContentLengthRejectsMalformedAndOverflowingValues() {
        assertInvalidContentLength(null);
        assertInvalidContentLength("");
        assertInvalidContentLength("+1");
        assertInvalidContentLength("-1");
        assertInvalidContentLength(" 1");
        assertInvalidContentLength("1 ");
        assertInvalidContentLength("1_0");
        assertInvalidContentLength("1, 2");
        assertInvalidContentLength("\u0661");
        assertInvalidContentLength("9223372036854775808");
    }

    private void assertInvalidCoordinate(String lat, String lng) {
        try {
            NetworkRequest.buildUrl(lat, lng);
            fail("Expected invalid coordinates to be rejected");
        } catch (IllegalArgumentException expected) {
            // Expected path.
        }
    }

    private void assertInvalidParams(String... params) {
        try {
            NetworkRequest.buildUrlFromParams(params);
            fail("Expected invalid async task parameters to be rejected");
        } catch (IllegalArgumentException expected) {
            // Expected path.
        }
    }

    private void assertInvalidMediaType(String contentType) {
        try {
            NetworkRequest.requireJsonMediaType(contentType);
            fail("Expected invalid response media type to be rejected");
        } catch (IOException expected) {
            // Expected path.
        }
    }

    private void assertInvalidContentLength(String contentLength) {
        try {
            NetworkRequest.parseContentLength(contentLength);
            fail("Expected invalid Content-Length to be rejected");
        } catch (IOException expected) {
            // Expected path.
        }
    }
}
