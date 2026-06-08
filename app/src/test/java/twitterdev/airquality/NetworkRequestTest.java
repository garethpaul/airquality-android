package twitterdev.airquality;

import org.junit.Test;

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

    private void assertInvalidCoordinate(String lat, String lng) {
        try {
            NetworkRequest.buildUrl(lat, lng);
            fail("Expected invalid coordinates to be rejected");
        } catch (IllegalArgumentException expected) {
            // Expected path.
        }
    }
}
