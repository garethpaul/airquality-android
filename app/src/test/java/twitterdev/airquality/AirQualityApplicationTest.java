package twitterdev.airquality;

import org.junit.Test;

import static org.junit.Assert.assertFalse;

public class AirQualityApplicationTest {
    @Test
    public void checkedInBuildLeavesTwitterKitUnconfigured() {
        assertFalse(AirQualityApplication.isTwitterKitConfigured());
    }
}
