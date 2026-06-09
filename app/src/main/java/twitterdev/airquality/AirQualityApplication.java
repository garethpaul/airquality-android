package twitterdev.airquality;

import android.app.Application;
import android.content.res.Configuration;
import android.util.Log;
import com.twitter.sdk.android.Twitter;
import com.twitter.sdk.android.core.TwitterAuthConfig;
import io.fabric.sdk.android.Fabric;

public class AirQualityApplication extends Application {
    private static final String TAG = "AirQualityApplication";
    private static final String TWITTER_KEY = "";
    private static final String TWITTER_SECRET = "";

    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
    }

    @Override
    public void onCreate() {
        super.onCreate();
        if (!hasTwitterCredentials()) {
            Log.w(TAG, "Twitter credentials unavailable; skipping Fabric initialization");
            return;
        }

        TwitterAuthConfig authConfig = new TwitterAuthConfig(TWITTER_KEY, TWITTER_SECRET);
        Fabric.with(this, new Twitter(authConfig));
    }

    private boolean hasTwitterCredentials() {
        return TWITTER_KEY.trim().length() > 0 && TWITTER_SECRET.trim().length() > 0;
    }

    @Override
    public void onLowMemory() {
        super.onLowMemory();
    }

    @Override
    public void onTerminate() {
        super.onTerminate();
    }

}
