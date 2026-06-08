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
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

public class NetworkRequest extends AsyncTask<String, Void, JSONObject> {
    private static final String TAG = NetworkRequest.class.getSimpleName();
    private static final String AIR_QUALITY_URL =
            "https://garethpaul-app.appspot.com/api/airquality";

    public static String buildUrl(String lat, String lng) {
        return AIR_QUALITY_URL + "?lat=" + lat + "&lng=" + lng;
    }

    static boolean hasCoordinateParameters(String... params) {
        return params != null
                && params.length >= 2
                && params[0] != null
                && params[1] != null;
    }

    @Override
    protected JSONObject doInBackground(String... params) {
        if (!hasCoordinateParameters(params)) {
            Log.e(TAG, "Missing latitude or longitude for air quality request");
            return null;
        }

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
            Log.e(TAG, "Air quality request failed with protocol error", e);
        } catch (IOException e) {
            Log.e(TAG, "Air quality request failed with network error", e);
        } catch (JSONException e) {
            Log.e(TAG, "Air quality response was not valid JSON", e);
        }
        return null;
    }

    protected void onPostExecute(JSONObject feed) {

    }
}
