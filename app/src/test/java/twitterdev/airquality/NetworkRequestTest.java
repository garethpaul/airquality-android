package twitterdev.airquality;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class NetworkRequestTest {
    @Test
    public void buildUrlIncludesLatitudeAndLongitude() {
        assertEquals(
                "https://garethpaul-app.appspot.com/api/airquality?lat=37.7&lng=-122.4",
                NetworkRequest.buildUrl("37.7", "-122.4"));
    }

    @Test
    public void hasCoordinateParametersRequiresLatitudeAndLongitude() {
        assertEquals(false, NetworkRequest.hasCoordinateParameters());
        assertEquals(false, NetworkRequest.hasCoordinateParameters("37.7"));
        assertEquals(false, NetworkRequest.hasCoordinateParameters(null, "-122.4"));
        assertEquals(false, NetworkRequest.hasCoordinateParameters("37.7", null));
        assertEquals(true, NetworkRequest.hasCoordinateParameters("37.7", "-122.4"));
    }
}
