package twitterdev.airquality;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.DownloadManager;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Color;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.location.Address;
import android.location.Criteria;
import android.location.Geocoder;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.provider.Settings;
import android.renderscript.Sampler;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.WindowManager;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.twitter.sdk.android.Twitter;
import com.twitter.sdk.android.core.TwitterAuthConfig;
import io.fabric.sdk.android.Fabric;
import org.apache.http.NameValuePair;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpConnectionParams;
import org.apache.http.params.HttpParams;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;


public class MainActivity extends Activity implements LocationListener, SensorEventListener {
    private static final String TAG = "MainActivity";
    private static final String DEFAULT_AIR_QUALITY_STATE = "Unknown";
    private static final String GOOD_AIR_QUALITY_STATE = "Good";

    private Context context;
    boolean isGPSEnabled = false;
    boolean isNetworkEnabled = false;
    boolean canGetLocation = false;
    Location location = null;
    double latitude;
    double longitude;
    private static final long MIN_DISTANCE_CHANGE_FOR_UPDATES = 10;
    private static final long MIN_TIME_BETWEEN_UPDATES = 1000 * 10 * 1;
    protected LocationManager locationManager;
    private SensorManager sensorManager;
    private String state = DEFAULT_AIR_QUALITY_STATE;
    private ImageView logo;
    private TextView text;
    private NetworkRequest airQualityRequest;
    private boolean locationUpdatesActive;

    @Override
    protected void onResume() {
        super.onResume();
        registerAccelerometerListener();
        if (location == null && airQualityRequest == null) {
            locationUpdatesActive = true;
            requestAirQualityForLocation(getLocation());
        }
    }

    @Override
    protected void onPause() {
        locationUpdatesActive = false;
        stopLocationUpdates();
        unregisterAccelerometerListener();
        super.onPause();
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        context = this;
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                WindowManager.LayoutParams.FLAG_FULLSCREEN);


        sensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);

        logo = (ImageView) findViewById(R.id.imageView);
        text = (TextView) findViewById(R.id.textView);
    }

    private void requestAirQualityForLocation(Location currentLocation) {
        if (currentLocation == null || !locationUpdatesActive) {
            return;
        }

        location = currentLocation;
        latitude = currentLocation.getLatitude();
        longitude = currentLocation.getLongitude();
        locationUpdatesActive = false;
        stopLocationUpdates();

        if (airQualityRequest != null) {
            airQualityRequest.cancel(true);
        }

        airQualityRequest = new NetworkRequest() {
            @Override
            protected void onPostExecute(JSONObject response) {
                if (airQualityRequest != this) {
                    return;
                }
                airQualityRequest = null;
                if (isCancelled() || isFinishing() || isDestroyed()) {
                    return;
                }
                state = readAirQualityState(response);
            }
        };
        airQualityRequest.execute(String.valueOf(latitude), String.valueOf(longitude));
    }

    private void stopLocationUpdates() {
        if (locationManager == null) {
            return;
        }

        try {
            locationManager.removeUpdates(this);
        } catch (SecurityException e) {
            Log.w(TAG, "Unable to stop location updates");
        }
    }

    @Override
    protected void onDestroy() {
        locationUpdatesActive = false;
        stopLocationUpdates();
        if (airQualityRequest != null) {
            airQualityRequest.cancel(true);
            airQualityRequest = null;
        }
        super.onDestroy();
    }

    private void registerAccelerometerListener() {
        if (sensorManager == null) {
            Log.w(TAG, "Sensor manager unavailable");
            return;
        }

        Sensor accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        if (accelerometer == null) {
            Log.w(TAG, "Accelerometer sensor unavailable");
            return;
        }

        sensorManager.registerListener(this, accelerometer, SensorManager.SENSOR_DELAY_NORMAL);
    }

    private void unregisterAccelerometerListener() {
        if (sensorManager != null) {
            sensorManager.unregisterListener(this);
        }
    }

    static String readAirQualityState(JSONObject response) {
        if (response == null) {
            return DEFAULT_AIR_QUALITY_STATE;
        }

        String airQuality = response.optString("air_quality", DEFAULT_AIR_QUALITY_STATE);
        if (airQuality.trim().length() == 0) {
            return DEFAULT_AIR_QUALITY_STATE;
        }

        return airQuality;
    }

    private void displayAccelerometer(SensorEvent event) {
        if (logo == null || text == null) {
            Log.w(TAG, "Air quality display views unavailable");
            return;
        }

        // Many sensors return 3 values, one for each axis.
        float x = event.values[0];
        float y = event.values[1];
        float z = event.values[2];

        if (z < 0){
            if (GOOD_AIR_QUALITY_STATE.equals(state)) {
                getWindow().getDecorView().setBackgroundColor(Color.GREEN);
                logo.setBackgroundResource(R.drawable.happy);
                text.setText("Air Quality Good");

            } else {
                getWindow().getDecorView().setBackgroundColor(Color.RED);
                logo.setBackgroundResource(R.drawable.sad);
                text.setText("Air Quality Bad");

            }


        } else {
            logo.setBackgroundResource(R.drawable.sky);
            getWindow().getDecorView().setBackgroundColor(Color.WHITE);
        }
    }

    public Location getLocation() {
        try {
            locationManager = (LocationManager) context
                    .getSystemService(LOCATION_SERVICE);
            if (locationManager == null) {
                Log.w(TAG, "Location manager unavailable");
                return location;
            }

            // getting GPS status
            isGPSEnabled = locationManager
                    .isProviderEnabled(LocationManager.GPS_PROVIDER);

            // getting network status
            isNetworkEnabled = locationManager
                    .isProviderEnabled(LocationManager.NETWORK_PROVIDER);

            if (!isGPSEnabled && !isNetworkEnabled) {
                // no network provider is enabled
            } else {
                this.canGetLocation = true;
                if (isNetworkEnabled) {
                    locationManager.requestLocationUpdates(
                            LocationManager.NETWORK_PROVIDER,
                            10,
                            MIN_DISTANCE_CHANGE_FOR_UPDATES, this);
                    Log.d("Network", "Network Enabled");
                    if (locationManager != null) {
                        location = locationManager
                                .getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
                        if (location == null) {
                            Log.d("Network", "not null");
                        }
                    }
                }
                // if GPS Enabled get lat/long using GPS Services
                if (isGPSEnabled) {
                    if (location == null) {
                        locationManager.requestLocationUpdates(
                                LocationManager.GPS_PROVIDER,
                                3,
                                MIN_DISTANCE_CHANGE_FOR_UPDATES, this);
                        Log.d("GPS", "GPS Enabled");
                        if (locationManager != null) {
                            location = locationManager
                                    .getLastKnownLocation(LocationManager.GPS_PROVIDER);
                        }
                    }
                }
            }

        } catch (Exception e) {
            Log.w(TAG, "Unable to read device location");
        }

        return location;
    }



    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @Override
    public void onLocationChanged(Location location) {
        requestAirQualityForLocation(location);
    }

    @Override
    public void onStatusChanged(String provider, int status, Bundle extras) {


    }

    @Override
    public void onProviderEnabled(String provider) {

    }

    @Override
    public void onProviderDisabled(String provider) {

    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        if (event == null || event.sensor == null || event.values == null
                || event.values.length < 3) {
            Log.w(TAG, "Ignoring malformed sensor event");
            return;
        }

        if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {

            displayAccelerometer(event);
        }


    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {

    }
}
