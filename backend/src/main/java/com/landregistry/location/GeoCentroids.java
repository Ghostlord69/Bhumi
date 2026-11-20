package com.landregistry.location;

import java.util.Map;

/** Approximate city/district centroids for Locate fallback (demo). */
public final class GeoCentroids {
    private static final Map<String, double[]> BY_CITY = Map.ofEntries(
            Map.entry("ballabgarh", new double[]{28.3590, 77.3120}),
            Map.entry("faridabad", new double[]{28.4089, 77.3178}),
            Map.entry("gurugram", new double[]{28.4595, 77.0266}),
            Map.entry("delhi", new double[]{28.6139, 77.2090}),
            Map.entry("noida", new double[]{28.5355, 77.3910}),
            Map.entry("lucknow", new double[]{26.8467, 80.9462}),
            Map.entry("mumbai", new double[]{19.0760, 72.8777}),
            Map.entry("pune", new double[]{18.5204, 73.8567}),
            Map.entry("bengaluru", new double[]{12.9716, 77.5946}),
            Map.entry("chennai", new double[]{13.0827, 80.2707}),
            Map.entry("hyderabad", new double[]{17.3850, 78.4867}),
            Map.entry("jaipur", new double[]{26.9124, 75.7873}),
            Map.entry("ahmedabad", new double[]{23.0225, 72.5714}),
            Map.entry("kolkata", new double[]{22.5726, 88.3639}),
            Map.entry("anantapur", new double[]{14.6819, 77.6006}),
            Map.entry("patna", new double[]{25.5941, 85.1376})
    );

    private GeoCentroids() {}

    public static double[] forCity(String city) {
        if (city == null) return null;
        return BY_CITY.get(city.trim().toLowerCase());
    }
}
