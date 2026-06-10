package twitterdev.airquality;

import android.os.AsyncTask;
import android.util.Log;

import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpConnectionParams;
import org.apache.http.params.HttpParams;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;

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

        return normalized;
    }

    private static String urlEncode(String value) {
        try {
            return URLEncoder.encode(value, "UTF-8");
        } catch (UnsupportedEncodingException e) {
            throw new IllegalStateException("UTF-8 must be available", e);
        }
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
        if (entity.getContentLength() > RESPONSE_MAX_BYTES) {
            throw new IOException("Air quality response is too large");
        }

        InputStream input = entity.getContent();
        try {
            ByteArrayOutputStream output = new ByteArrayOutputStream();
            byte[] buffer = new byte[4096];
            int totalBytes = 0;
            int bytesRead;
            while ((bytesRead = input.read(buffer)) != -1) {
                totalBytes += bytesRead;
                if (totalBytes > RESPONSE_MAX_BYTES) {
                    throw new IOException("Air quality response is too large");
                }
                output.write(buffer, 0, bytesRead);
            }
            return output.toString("UTF-8");
        } finally {
            input.close();
        }
    }

    @Override
    protected JSONObject doInBackground(String... params) {
        try {
            String url = buildUrlFromParams(params);

            HttpParams httpParams = new BasicHttpParams();
            HttpConnectionParams.setConnectionTimeout(httpParams,
                    REQUEST_TIMEOUT_MILLIS);
            HttpConnectionParams.setSoTimeout(httpParams, REQUEST_TIMEOUT_MILLIS);

            // Instantiate an HttpClient
            HttpClient httpclient = new DefaultHttpClient(httpParams);
            HttpGet httpget = new HttpGet(url);

            try {
                //Log.i(getClass().getSimpleName(), "send  task - start");
                HttpResponse response = httpclient.execute(httpget);
                String responseBody = readResponseBody(response);
                JSONObject json = new JSONObject(responseBody);
                return json;


            } catch (ClientProtocolException e) {
                Log.w(TAG, "Air quality request failed", e);
            } catch (IOException e) {
                Log.w(TAG, "Air quality request failed", e);
            } catch (JSONException e) {
                Log.w(TAG, "Invalid air quality response JSON", e);
            } finally {
                httpclient.getConnectionManager().shutdown();
            }


        } catch (IllegalArgumentException e) {
            Log.w(TAG, "Invalid air quality request parameters", e);
        }
        return null;
    }

    protected void onPostExecute(JSONObject feed) {

    }
}
