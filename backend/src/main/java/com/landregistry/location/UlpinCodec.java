package com.landregistry.location;

/** ULPIN encode/decode aligned with ai-service/src/ulpin_codec.py */
public final class UlpinCodec {
    private static final String BASE14 = "0123456789ABCD";
    private static final String BASE19_LONG = "0123456789ABCDEFGHI";
    private static final String BASE32 = "0123456789ABCDEFGHIJKLMNOPQRSTUV";
    private static final int FLOOR_BIAS = 544;

    private UlpinCodec() {}

    public static String encode(double latitude, double longitude) {
        return encode(latitude, longitude, 0);
    }

    public static String encode(double latitude, double longitude, int floorLevel) {
        int[] lat = split(latitude);
        int[] lon = split(longitude);
        int latShifted = Math.abs(lat[0]) + 90;
        int lonShifted = Math.abs(lon[0]) + 180;
        String latFrac = String.format("%06d", lat[1]);
        String lonFrac = String.format("%06d", lon[1]);
        String lat1 = subst(toBase(latShifted, BASE14, 2));
        String lat3 = subst(toBase(Integer.parseInt(latFrac.substring(0, 3)), BASE32, 2));
        String lat4 = subst(toBase(Integer.parseInt(latFrac.substring(3, 6)), BASE32, 2));
        String long1 = subst(toBase(lonShifted, BASE19_LONG, 2));
        String long3 = subst(toBase(Integer.parseInt(lonFrac.substring(0, 3)), BASE32, 2));
        String long4 = subst(toBase(Integer.parseInt(lonFrac.substring(3, 6)), BASE32, 2));
        String f1 = subst(toBase(floorLevel + FLOOR_BIAS, BASE32, 2));
        return lat1 + lat3 + lat4 + long1 + long3 + long4 + f1;
    }

    public static double[] decode(String ulpin) {
        if (ulpin == null) return null;
        String raw = ulpin.replaceAll("[^A-Za-z0-9]", "").toUpperCase();
        if (raw.length() != 14) return null;
        try {
            int latShifted = fromBase(unsubst(raw.substring(0, 2)), BASE14);
            int lat3 = fromBase(unsubst(raw.substring(2, 4)), BASE32);
            int lat4 = fromBase(unsubst(raw.substring(4, 6)), BASE32);
            int lonShifted = fromBase(unsubst(raw.substring(6, 8)), BASE19_LONG);
            int lon3 = fromBase(unsubst(raw.substring(8, 10)), BASE32);
            int lon4 = fromBase(unsubst(raw.substring(10, 12)), BASE32);
            int latWhole = latShifted - 90;
            int lonWhole = lonShifted - 180;
            double lat = Double.parseDouble(latWhole + "." + String.format("%03d%03d", lat3, lat4));
            double lon = Double.parseDouble(lonWhole + "." + String.format("%03d%03d", lon3, lon4));
            return new double[]{lat, lon};
        } catch (Exception e) {
            return null;
        }
    }

    public static String locateUrl(double lat, double lon) {
        return String.format("https://www.google.com/maps?q=%.6f,%.6f", lat, lon);
    }

    private static int[] split(double value) {
        double v = Math.abs(value);
        String s = String.format(java.util.Locale.US, "%.6f", v);
        String[] parts = s.split("\\.");
        int whole = Integer.parseInt(parts[0]);
        int frac = Integer.parseInt(parts[1]);
        if (value < 0) whole = -whole;
        return new int[]{whole, frac};
    }

    private static String toBase(int n, String alphabet, int width) {
        int base = alphabet.length();
        StringBuilder sb = new StringBuilder();
        int x = Math.max(0, n);
        if (x == 0) sb.append(alphabet.charAt(0));
        while (x > 0) {
            sb.append(alphabet.charAt(x % base));
            x /= base;
        }
        String s = sb.reverse().toString();
        while (s.length() < width) s = alphabet.charAt(0) + s;
        return s.substring(s.length() - width);
    }

    private static int fromBase(String s, String alphabet) {
        int n = 0;
        int base = alphabet.length();
        for (int i = 0; i < s.length(); i++) {
            n = n * base + alphabet.indexOf(s.charAt(i));
        }
        return n;
    }

    private static String subst(String s) {
        return s.replace('I', 'Y').replace('O', 'Z');
    }

    private static String unsubst(String s) {
        return s.replace('Y', 'I').replace('Z', 'O');
    }
}
