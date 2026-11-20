package com.landregistry.location;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import org.junit.jupiter.api.Test;

class UlpinCodecTest {
    @Test
    void encodesKnownExample() {
        assertEquals("832454DYJFAQH0", UlpinCodec.encode(25.068164, 85.623346));
    }

    @Test
    void decodeRoundTripNearExample() {
        double[] decoded = UlpinCodec.decode("832454DYJFAQH0");
        assertNotNull(decoded);
        assertEquals(25.068164, decoded[0], 0.000001);
        assertEquals(85.623346, decoded[1], 0.000001);
    }
}
