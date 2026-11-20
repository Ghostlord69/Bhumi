package com.landregistry.location;

import java.util.LinkedHashMap;
import java.util.Map;

/** Indian vehicle RTO state/UT codes for seeded admin logins. */
public final class StateCodes {
    private static final Map<String, String> BY_STATE = new LinkedHashMap<>();

    static {
        BY_STATE.put("Andhra Pradesh", "AP");
        BY_STATE.put("Arunachal Pradesh", "AR");
        BY_STATE.put("Assam", "AS");
        BY_STATE.put("Bihar", "BR");
        BY_STATE.put("Chhattisgarh", "CG");
        BY_STATE.put("Goa", "GA");
        BY_STATE.put("Gujarat", "GJ");
        BY_STATE.put("Haryana", "HR");
        BY_STATE.put("Himachal Pradesh", "HP");
        BY_STATE.put("Jharkhand", "JH");
        BY_STATE.put("Karnataka", "KA");
        BY_STATE.put("Kerala", "KL");
        BY_STATE.put("Madhya Pradesh", "MP");
        BY_STATE.put("Maharashtra", "MH");
        BY_STATE.put("Manipur", "MN");
        BY_STATE.put("Meghalaya", "ML");
        BY_STATE.put("Mizoram", "MZ");
        BY_STATE.put("Nagaland", "NL");
        BY_STATE.put("Odisha", "OD");
        BY_STATE.put("Punjab", "PB");
        BY_STATE.put("Rajasthan", "RJ");
        BY_STATE.put("Sikkim", "SK");
        BY_STATE.put("Tamil Nadu", "TN");
        BY_STATE.put("Telangana", "TS");
        BY_STATE.put("Tripura", "TR");
        BY_STATE.put("Uttar Pradesh", "UP");
        BY_STATE.put("Uttarakhand", "UK");
        BY_STATE.put("West Bengal", "WB");
        BY_STATE.put("Andaman and Nicobar Islands", "AN");
        BY_STATE.put("Chandigarh", "CH");
        BY_STATE.put("Dadra and Nagar Haveli and Daman and Diu", "DD");
        BY_STATE.put("Delhi", "DL");
        BY_STATE.put("Jammu and Kashmir", "JK");
        BY_STATE.put("Ladakh", "LA");
        BY_STATE.put("Lakshadweep", "LD");
        BY_STATE.put("Puducherry", "PY");
    }

    private StateCodes() {}

    public static Map<String, String> all() {
        return Map.copyOf(BY_STATE);
    }

    public static String codeFor(String state) {
        return BY_STATE.get(state);
    }

    public static String reverse(String code) {
        return new StringBuilder(code).reverse().toString();
    }

    public static String adminEmail(String rtoCode) {
        return rtoCode + "12345" + reverse(rtoCode) + "@bhumi.gov.in";
    }

    public static String adminPassword(String rtoCode) {
        return "Admin" + rtoCode + "123@";
    }
}
