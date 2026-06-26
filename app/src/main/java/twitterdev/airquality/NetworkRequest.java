package twitterdev.airquality;

import android.os.AsyncTask;
import android.util.Log;

import org.apache.http.Header;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.params.HttpClientParams;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpConnectionParams;
import org.apache.http.params.HttpParams;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.nio.ByteBuffer;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.util.Locale;

public class NetworkRequest extends AsyncTask<String, Void, JSONObject> {
    private static final String TAG = "NetworkRequest";
    private static final int REQUEST_TIMEOUT_MILLIS = 1000;
    private static final int RESPONSE_MAX_BYTES = 1024 * 1024;
    private static final String AIR_QUALITY_URL =
            "https://garethpaul-app.appspot.com/api/airquality";

    public static String buildUrl(String lat, String lng) {
        String normalizedLat = normalizeCoordinate(lat, "lat", -90.0, 90.0);
        String normalizedLng = normalizeCoordinate(lng, "lng", -180.0, 180.0);
        return AIR_QUALITY_URL
                + "?lat=" + urlEncode(normalizedLat)
                + "&lng=" + urlEncode(normalizedLng);
    }

    public static String buildUrlFromParams(String... params) {
        if (params == null || params.length < 2) {
            throw new IllegalArgumentException("lat and lng are required");
        }

        return buildUrl(params[0], params[1]);
    }

    private static String normalizeCoordinate(
            String value, String name, double min, double max) {
        if (value == null) {
            throw new IllegalArgumentException(name + " is required");
        }

        String normalized = value.trim();
        if (normalized.length() == 0) {
            throw new IllegalArgumentException(name + " is required");
        }

        double coordinate;
        try {
            coordinate = Double.parseDouble(normalized);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException(name + " must be numeric");
        }

        if (Double.isNaN(coordinate) || Double.isInfinite(coordinate)) {
            throw new IllegalArgumentException(name + " must be finite");
        }

        if (coordinate < min || coordinate > max) {
            throw new IllegalArgumentException(name + " is outside the supported range");
        }

        if (coordinate == 0.0d) {
            return "0.0";
        }
        return Double.toString(coordinate);
    }

    private static String urlEncode(String value) {
        try {
            return URLEncoder.encode(value, "UTF-8");
        } catch (UnsupportedEncodingException e) {
            throw new IllegalStateException("UTF-8 must be available", e);
        }
    }

    static String decodeUtf8(byte[] bytes) throws IOException {
        return StandardCharsets.UTF_8.newDecoder()
                .onMalformedInput(CodingErrorAction.REPORT)
                .onUnmappableCharacter(CodingErrorAction.REPORT)
                .decode(ByteBuffer.wrap(bytes))
                .toString();
    }

    static void requireJsonMediaType(String contentType) throws IOException {
        if (contentType == null) {
            throw new IOException("Air quality response media type is invalid");
        }

        int parameterStart = contentType.indexOf(';');
        String mediaType = (parameterStart >= 0
                ? contentType.substring(0, parameterStart)
                : contentType);
        mediaType = trimHttpWhitespace(mediaType).toLowerCase(Locale.US);
        int separator = mediaType.indexOf('/');
        if (separator <= 0 || separator != mediaType.lastIndexOf('/')) {
            throw new IOException("Air quality response media type is invalid");
        }

        String type = mediaType.substring(0, separator);
        String subtype = mediaType.substring(separator + 1);
        boolean jsonSubtype = "json".equals(subtype)
                || (subtype.length() > "+json".length() && subtype.endsWith("+json"));
        if (!"application".equals(type)
                || !isMimeToken(type)
                || !isMimeToken(subtype)
                || !jsonSubtype) {
            throw new IOException("Air quality response media type is invalid");
        }

        requireUtf8MediaTypeParameters(contentType, parameterStart);
    }

    static void requireSingleJsonMediaType(String... contentTypes) throws IOException {
        if (contentTypes == null || contentTypes.length != 1) {
            throw new IOException("Air quality response media type is invalid");
        }
        requireJsonMediaType(contentTypes[0]);
    }

    private static void requireUtf8MediaTypeParameters(
            String contentType, int parameterStart) throws IOException {
        if (parameterStart < 0) {
            return;
        }

        boolean charsetSeen = false;
        int index = parameterStart + 1;
        while (index < contentType.length()) {
            index = skipHttpWhitespace(contentType, index);
            int nameStart = index;
            while (index < contentType.length()
                    && contentType.charAt(index) != '='
                    && contentType.charAt(index) != ';') {
                index++;
            }
            if (index >= contentType.length() || contentType.charAt(index) != '=') {
                throw new IOException("Air quality response media type is invalid");
            }

            String name = trimHttpWhitespace(contentType.substring(nameStart, index))
                    .toLowerCase(Locale.US);
            if (!isMimeToken(name)) {
                throw new IOException("Air quality response media type is invalid");
            }

            index = skipHttpWhitespace(contentType, index + 1);
            StringBuilder value = new StringBuilder();
            if (index < contentType.length() && contentType.charAt(index) == '"') {
                index = readQuotedParameter(contentType, index + 1, value);
            } else {
                int valueStart = index;
                while (index < contentType.length() && contentType.charAt(index) != ';') {
                    index++;
                }
                String tokenValue = trimHttpWhitespace(
                        contentType.substring(valueStart, index));
                if (!isMimeToken(tokenValue.toLowerCase(Locale.US))) {
                    throw new IOException("Air quality response media type is invalid");
                }
                value.append(tokenValue);
            }

            if ("charset".equals(name)) {
                String normalizedValue = value.substring(0).toLowerCase(Locale.US);
                if (charsetSeen
                        || !"utf-8".equals(normalizedValue)) {
                    throw new IOException("Air quality response media type is invalid");
                }
                charsetSeen = true;
            }

            index = skipHttpWhitespace(contentType, index);
            if (index == contentType.length()) {
                return;
            }
            if (contentType.charAt(index) != ';') {
                throw new IOException("Air quality response media type is invalid");
            }
            index++;
        }

        throw new IOException("Air quality response media type is invalid");
    }

    private static int readQuotedParameter(
            String contentType, int index, StringBuilder value) throws IOException {
        while (index < contentType.length()) {
            char character = contentType.charAt(index++);
            if (character == '"') {
                return index;
            }
            if (character == '\\') {
                if (index >= contentType.length()) {
                    throw new IOException("Air quality response media type is invalid");
                }
                character = contentType.charAt(index++);
            }
            if ((character < 0x20 && character != '\t') || character == 0x7f) {
                throw new IOException("Air quality response media type is invalid");
            }
            value.append(character);
        }
        throw new IOException("Air quality response media type is invalid");
    }

    private static int skipHttpWhitespace(String value, int index) {
        while (index < value.length()
                && (value.charAt(index) == ' ' || value.charAt(index) == '\t')) {
            index++;
        }
        return index;
    }

    private static String trimHttpWhitespace(String value) {
        int start = skipHttpWhitespace(value, 0);
        int end = value.length();
        while (end > start
                && (value.charAt(end - 1) == ' ' || value.charAt(end - 1) == '\t')) {
            end--;
        }
        return value.substring(start, end);
    }

    static long parseContentLength(String contentLength) throws IOException {
        if (contentLength == null || contentLength.length() == 0) {
            throw new IOException("Air quality response Content-Length is invalid");
        }

        long parsedLength = 0;
        for (int index = 0; index < contentLength.length(); index++) {
            char character = contentLength.charAt(index);
            if (character < '0' || character > '9') {
                throw new IOException("Air quality response Content-Length is invalid");
            }
            int digit = character - '0';
            if (parsedLength > (Long.MAX_VALUE - digit) / 10) {
                throw new IOException("Air quality response Content-Length is invalid");
            }
            parsedLength = parsedLength * 10 + digit;
        }
        return parsedLength;
    }

    static String readBoundedUtf8(InputStream input) throws IOException {
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        byte[] buffer = new byte[4096];
        int totalBytes = 0;
        int bytesRead;
        while ((bytesRead = input.read(buffer)) != -1) {
            if (bytesRead == 0) {
                throw new IOException("Air quality response read made no progress");
            }
            totalBytes += bytesRead;
            if (totalBytes > RESPONSE_MAX_BYTES) {
                throw new IOException("Air quality response is too large");
            }
            output.write(buffer, 0, bytesRead);
        }
        return decodeUtf8(output.toByteArray());
    }

    private static boolean isMimeToken(String value) {
        if (value.length() == 0) {
            return false;
        }

        for (int index = 0; index < value.length(); index++) {
            char character = value.charAt(index);
            if (!((character >= 'a' && character <= 'z')
                    || (character >= '0' && character <= '9')
                    || "!#$%&'*+-.^_`|~".indexOf(character) >= 0)) {
                return false;
            }
        }
        return true;
    }

    static String readResponseBody(HttpResponse response) throws IOException {
        int statusCode = response.getStatusLine().getStatusCode();
        if (statusCode < 200 || statusCode >= 300) {
            throw new ClientProtocolException("Unexpected HTTP status");
        }

        HttpEntity entity = response.getEntity();
        if (entity == null) {
            throw new IOException("Air quality response body is missing");
        }
        Header[] contentTypeHeaders = response.getHeaders("Content-Type");
        String[] contentTypes = new String[contentTypeHeaders.length];
        for (int index = 0; index < contentTypeHeaders.length; index++) {
            contentTypes[index] = contentTypeHeaders[index].getValue();
        }
        requireSingleJsonMediaType(contentTypes);
        Header[] contentLengthHeaders = response.getHeaders("Content-Length");
        if (contentLengthHeaders.length > 1) {
            throw new IOException("Air quality response Content-Length is invalid");
        }
        long contentLength = contentLengthHeaders.length == 1
                ? parseContentLength(contentLengthHeaders[0].getValue())
                : entity.getContentLength();
        if (contentLength < -1) {
            throw new IOException("Air quality response Content-Length is invalid");
        }
        if (contentLength > RESPONSE_MAX_BYTES) {
            throw new IOException("Air quality response is too large");
        }

        InputStream input = entity.getContent();
        try {
            return readBoundedUtf8(input);
        } finally {
            input.close();
        }
    }

    static JSONObject parseJsonObject(String responseBody) throws JSONException {
        JSONTokener tokener = new JSONTokener(responseBody);
        Object value = tokener.nextValue();
        if (!(value instanceof JSONObject)) {
            throw new JSONException("Air quality response must contain one JSON object");
        }
        while (tokener.more()) {
            if (!isJsonWhitespace(tokener.next())) {
                throw new JSONException("Air quality response contains trailing content");
            }
        }
        return (JSONObject) value;
    }

    static boolean isJsonWhitespace(char character) {
        return character == ' ' || character == '\t'
                || character == '\r' || character == '\n';
    }

    @Override
    protected JSONObject doInBackground(String... params) {
        try {
            String url = buildUrlFromParams(params);

            HttpParams httpParams = new BasicHttpParams();
            HttpConnectionParams.setConnectionTimeout(httpParams,
                    REQUEST_TIMEOUT_MILLIS);
            HttpConnectionParams.setSoTimeout(httpParams, REQUEST_TIMEOUT_MILLIS);
            HttpClientParams.setRedirecting(httpParams, false);

            // Instantiate an HttpClient
            HttpClient httpclient = new DefaultHttpClient(httpParams);
            HttpGet httpget = new HttpGet(url);

            try {
                //Log.i(getClass().getSimpleName(), "send  task - start");
                HttpResponse response = httpclient.execute(httpget);
                String responseBody = readResponseBody(response);
                JSONObject json = parseJsonObject(responseBody);
                return json;


            } catch (ClientProtocolException e) {
                Log.w(TAG, "Air quality request failed");
            } catch (IOException e) {
                Log.w(TAG, "Air quality request failed");
            } catch (JSONException e) {
                Log.w(TAG, "Invalid air quality response JSON");
            } finally {
                httpclient.getConnectionManager().shutdown();
            }


        } catch (IllegalArgumentException e) {
            Log.w(TAG, "Invalid air quality request parameters");
        }
        return null;
    }

    protected void onPostExecute(JSONObject feed) {

    }
}
