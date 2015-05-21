package twitterdev.airquality;

import android.app.Activity;
import android.content.Context;
import android.os.Bundle;

import com.twitter.sdk.android.Twitter;
import android.content.Intent;
import android.util.Log;
import android.widget.Toast;

import com.twitter.sdk.android.core.Callback;
import com.twitter.sdk.android.core.Result;
import com.twitter.sdk.android.core.TwitterException;
import com.twitter.sdk.android.core.TwitterSession;
import com.twitter.sdk.android.core.identity.TwitterLoginButton;

public class LoginActivity extends Activity {
    // Note: Your consumer key and secret should be obfuscated in your source code before shipping.

    private TwitterLoginButton loginButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        TwitterSession currentSession = Twitter.getSessionManager().getActiveSession();
        if (currentSession == null) {
            loginButton = (TwitterLoginButton) findViewById(R.id.twitter_login_button);
            loginButton.setCallback(new Callback<TwitterSession>() {
                @Override
                public void success(Result<TwitterSession> result) {
                    Log.v("Login", "Success");
                    // Do something with result, which provides a TwitterSession for making API calls
                    moveToLogin();
                }

                @Override
                public void failure(TwitterException exception) {
                    // Do something on failure
                    Context context = getApplicationContext();
                    CharSequence text = "Wow! Something went wrong here oops.";
                    int duration = Toast.LENGTH_SHORT;

                    Toast toast = Toast.makeText(context, text, duration);
                    toast.show();
                }
            });
        } else {
            moveToLogin();
        }
    }

    private void moveToLogin(){
        Intent intent = new Intent(getApplicationContext(), MainActivity.class);
        startActivity(intent);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        loginButton.onActivityResult(requestCode, resultCode, data);
    }

}
