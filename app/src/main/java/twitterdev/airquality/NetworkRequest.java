package twitterdev.airquality;

import android.os.AsyncTask;
import android.util.Log;

import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpConnectionParams;
import org.apache.http.params.HttpParams;
import org.json.JSONObject;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;

public class NetworkRequest extends AsyncTask<String, Void, JSONObject> {
    private static final String AIR_QUALITY_URL =
            "https://garethpaul-app.appspot.com/api/airquality";

    public static String buildUrl(String lat, String lng) {
        String normalizedLat = normalizeCoordinate(lat, "lat", -90.0, 90.0);
        String normalizedLng = normalizeCoordinate(lng, "lng", -180.0, 180.0);
        return AIR_QUALITY_URL
                + "?lat=" + urlEncode(normalizedLat)
                + "&lng=" + urlEncode(normalizedLng);
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

    @Override
    protected JSONObject doInBackground(String... params) {
        try {
            String lat, lng;
            lat = params[0];
            lng = params[1];

            HttpParams httpParams = new BasicHttpParams();
            HttpConnectionParams.setConnectionTimeout(httpParams,
                    1000);
            HttpConnectionParams.setSoTimeout(httpParams, 1000);
            //
            HttpParams p = new BasicHttpParams();
            // p.setParameter("name", pvo.getName());
            p.setParameter("user", "1");

            // Instantiate an HttpClient
            HttpClient httpclient = new DefaultHttpClient(p);
            String url = buildUrl(lat, lng);
            HttpGet httpget = new HttpGet(url);

            try {
                //Log.i(getClass().getSimpleName(), "send  task - start");
                ResponseHandler<String> responseHandler = new BasicResponseHandler();
                String responseBody = httpclient.execute(httpget,
                        responseHandler);
                JSONObject json = new JSONObject(responseBody);
                return json;


            } catch (ClientProtocolException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }


        } catch (Throwable t) {

        }
        return null;
    }

    protected void onPostExecute(JSONObject feed) {

    }
}
