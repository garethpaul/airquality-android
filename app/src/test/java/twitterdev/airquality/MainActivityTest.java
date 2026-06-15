package twitterdev.airquality;

import org.json.JSONArray;
import org.json.JSONObject;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class MainActivityTest {
    @Test
    public void readAirQualityStatePreservesNonblankStrings() throws Exception {
        assertEquals("Good", MainActivity.readAirQualityState(responseWith("Good")));
        assertEquals("Moderate", MainActivity.readAirQualityState(responseWith("Moderate")));
    }

    @Test
    public void readAirQualityStateTrimsNonblankStrings() throws Exception {
        assertEquals("Good", MainActivity.readAirQualityState(responseWith("  Good \t")));
        assertEquals("Moderate", MainActivity.readAirQualityState(responseWith("\nModerate ")));
    }

    @Test
    public void readAirQualityStateDefaultsMissingNullBlankAndNonStringValues()
            throws Exception {
        assertUnknown(null);
        assertUnknown(new JSONObject());
        assertUnknown(responseWith(JSONObject.NULL));
        assertUnknown(responseWith(""));
        assertUnknown(responseWith("   "));
        assertUnknown(responseWith(true));
        assertUnknown(responseWith(42));
        assertUnknown(responseWith(new JSONObject().put("nested", "value")));
        assertUnknown(responseWith(new JSONArray().put("Good")));
    }

    private static JSONObject responseWith(Object value) throws Exception {
        return new JSONObject().put("air_quality", value);
    }

    private static void assertUnknown(JSONObject response) {
        assertEquals("Unknown", MainActivity.readAirQualityState(response));
    }
}
