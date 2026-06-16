package twitterdev.airquality;

import org.junit.Test;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
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
    public void readBoundedUtf8AccumulatesFragmentedReads() throws IOException {
        assertEquals(
                "{\"air_quality\":\"good\"}",
                NetworkRequest.readBoundedUtf8(
                        new FragmentedInputStream(
                                "{\"air_quality\":\"good\"}"
                                        .getBytes(StandardCharsets.UTF_8),
                                3)));
    }

    @Test
    public void readBoundedUtf8RejectsZeroProgress() {
        try {
            NetworkRequest.readBoundedUtf8(new ZeroProgressInputStream());
            fail("Expected a zero-progress response read to be rejected");
        } catch (IOException expected) {
            // Expected path.
        }
    }

    @Test
    public void readBoundedUtf8AcceptsExactResponseLimit() throws IOException {
        byte[] body = new byte[1024 * 1024];
        assertEquals(body.length, NetworkRequest.readBoundedUtf8(
                new ByteArrayInputStream(body)).length());
    }

    @Test
    public void readBoundedUtf8RejectsResponseOverLimit() {
        try {
            NetworkRequest.readBoundedUtf8(
                    new ByteArrayInputStream(new byte[(1024 * 1024) + 1]));
            fail("Expected an oversized response to be rejected");
        } catch (IOException expected) {
            // Expected path.
        }
    }

    @Test
    public void requireJsonMediaTypeAcceptsJsonApplicationTypes() throws IOException {
        NetworkRequest.requireJsonMediaType("Application/JSON; charset=UTF-8");
        NetworkRequest.requireJsonMediaType("application/json; charset=\"utf-8\"");
        NetworkRequest.requireJsonMediaType("application/json; profile=v1");
        NetworkRequest.requireJsonMediaType(
                "application/json ; profile=\"https://example.test/schema;a=b\" ; "
                        + "charset = \"UTF-8\"");
        NetworkRequest.requireJsonMediaType(
                "application/json; profile=\"https://example.test/schema,a=b\"");
        NetworkRequest.requireJsonMediaType(
                " \tapplication/json\t ;\tcharset\t=\tUTF-8\t");
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
        assertInvalidMediaType("application/json;");
        assertInvalidMediaType("application/json; charset");
        assertInvalidMediaType("application/json; charset=");
        assertInvalidMediaType("application/json; profile=");
        assertInvalidMediaType("application/json; charset=ISO-8859-1");
        assertInvalidMediaType("application/json; charset=UTF-8; charset=UTF-8");
        assertInvalidMediaType("application/json; charset=UTF-8; charset=ISO-8859-1");
        assertInvalidMediaType("application/json; profile=\"unterminated");
        assertInvalidMediaType("text/json");
        assertInvalidMediaType("text/html");
    }

    @Test
    public void requireJsonMediaTypeRejectsControlsOutsideQuotedValues() {
        assertInvalidMediaType("\rapplication/json");
        assertInvalidMediaType("\napplication/json");
        assertInvalidMediaType("\u000bapplication/json");
        assertInvalidMediaType("\u000capplication/json");
        assertInvalidMediaType("application/json\r");
        assertInvalidMediaType("application/json\n");
        assertInvalidMediaType("application/json;\rcharset=UTF-8");
        assertInvalidMediaType("application/json;\ncharset=UTF-8");
        assertInvalidMediaType("application/json;\u000bcharset=UTF-8");
        assertInvalidMediaType("application/json;\u000ccharset=UTF-8");
        assertInvalidMediaType("application/json; charset=\rUTF-8");
        assertInvalidMediaType("application/json; charset=UTF-8\n");
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

    @Test
    public void requireSingleJsonMediaTypeRejectsAmbiguousHeaders() throws IOException {
        NetworkRequest.requireSingleJsonMediaType("application/json");
        assertInvalidResponseMediaType();
        assertInvalidResponseMediaType("application/json", "application/json");
        assertInvalidResponseMediaType("application/json", "text/html");
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

    private void assertInvalidResponseMediaType(String... contentTypes) {
        try {
            NetworkRequest.requireSingleJsonMediaType(contentTypes);
            fail("Expected ambiguous response media type headers to be rejected");
        } catch (IOException expected) {
            // Expected path.
        }
    }

    private static final class FragmentedInputStream extends InputStream {
        private final byte[] bytes;
        private final int fragmentSize;
        private int offset;

        FragmentedInputStream(byte[] bytes, int fragmentSize) {
            this.bytes = bytes;
            this.fragmentSize = fragmentSize;
        }

        @Override
        public int read() {
            if (offset >= bytes.length) {
                return -1;
            }
            return bytes[offset++] & 0xff;
        }

        @Override
        public int read(byte[] buffer, int bufferOffset, int length) {
            if (offset >= bytes.length) {
                return -1;
            }
            int bytesRead = Math.min(Math.min(length, fragmentSize), bytes.length - offset);
            System.arraycopy(bytes, offset, buffer, bufferOffset, bytesRead);
            offset += bytesRead;
            return bytesRead;
        }
    }

    private static final class ZeroProgressInputStream extends InputStream {
        @Override
        public int read() {
            return 0;
        }

        @Override
        public int read(byte[] buffer, int offset, int length) {
            return 0;
        }
    }
}
