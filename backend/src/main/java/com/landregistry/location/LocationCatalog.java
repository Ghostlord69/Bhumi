package com.landregistry.location;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Component;

@Component
public class LocationCatalog {

    public static final List<String> STATES = List.of(
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
            "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
            "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
            "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
            "West Bengal",
            "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
            "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
    );

    private final Map<String, Map<String, List<String>>> tree = new LinkedHashMap<>();

    public LocationCatalog() {
        // Detailed demo trees
        put("Haryana", "Faridabad", List.of("Faridabad", "Ballabgarh", "Greater Faridabad"));
        put("Haryana", "Gurugram", List.of("Gurugram", "Sohna", "Pataudi"));
        put("Haryana", "Hisar", List.of("Hisar", "Hansi"));
        put("Haryana", "Karnal", List.of("Karnal", "Nilokheri"));
        put("Haryana", "Ambala", List.of("Ambala", "Naraingarh"));
        put("Delhi", "New Delhi", List.of("Connaught Place", "Chanakyapuri"));
        put("Delhi", "South Delhi", List.of("Saket", "Hauz Khas"));
        put("Delhi", "North Delhi", List.of("Civil Lines", "Model Town"));
        put("Delhi", "East Delhi", List.of("Laxmi Nagar", "Mayur Vihar"));
        put("Uttar Pradesh", "Gautam Buddha Nagar", List.of("Noida", "Greater Noida"));
        put("Uttar Pradesh", "Lucknow", List.of("Lucknow", "Gomti Nagar"));
        put("Uttar Pradesh", "Varanasi", List.of("Varanasi", "Ramnagar"));
        put("Uttar Pradesh", "Agra", List.of("Agra", "Fatehpur Sikri"));
        put("Maharashtra", "Mumbai Suburban", List.of("Andheri", "Bandra", "Borivali"));
        put("Maharashtra", "Pune", List.of("Pune", "Hinjewadi", "Hadapsar"));
        put("Maharashtra", "Nagpur", List.of("Nagpur", "Kamptee"));
        put("Karnataka", "Bengaluru Urban", List.of("Bengaluru", "Whitefield", "Electronic City"));
        put("Karnataka", "Mysuru", List.of("Mysuru", "Nanjangud"));
        put("Rajasthan", "Jaipur", List.of("Jaipur", "Sanganer"));
        put("Rajasthan", "Jodhpur", List.of("Jodhpur", "Bilara"));
        put("Gujarat", "Ahmedabad", List.of("Ahmedabad", "Bopal"));
        put("Gujarat", "Surat", List.of("Surat", "Adajan"));
        put("Tamil Nadu", "Chennai", List.of("Chennai", "Tambaram"));
        put("Tamil Nadu", "Coimbatore", List.of("Coimbatore", "Pollachi"));
        put("West Bengal", "Kolkata", List.of("Kolkata", "Salt Lake"));
        put("West Bengal", "Howrah", List.of("Howrah", "Bally"));
        put("Telangana", "Hyderabad", List.of("Hyderabad", "Secunderabad"));
        put("Telangana", "Rangareddy", List.of("Shamshabad", "Ibrahimpatnam"));
        put("Punjab", "Ludhiana", List.of("Ludhiana", "Khanna"));
        put("Punjab", "Amritsar", List.of("Amritsar", "Ajnala"));
        put("Bihar", "Patna", List.of("Patna", "Danapur"));
        put("Bihar", "Gaya", List.of("Gaya", "Bodh Gaya"));
        put("Odisha", "Khordha", List.of("Bhubaneswar", "Jatni"));
        put("Odisha", "Cuttack", List.of("Cuttack", "Choudwar"));
        put("Madhya Pradesh", "Bhopal", List.of("Bhopal", "Berasia"));
        put("Madhya Pradesh", "Indore", List.of("Indore", "Mhow"));
        put("Kerala", "Ernakulam", List.of("Kochi", "Aluva"));
        put("Kerala", "Thiruvananthapuram", List.of("Thiruvananthapuram", "Neyyattinkara"));
        put("Andhra Pradesh", "Anantapur", List.of("Anantapur", "Anantapur Rural"));
        put("Andhra Pradesh", "Visakhapatnam", List.of("Visakhapatnam", "Gajuwaka"));
        put("Assam", "Kamrup Metropolitan", List.of("Guwahati", "Dispur"));
        put("Assam", "Dibrugarh", List.of("Dibrugarh", "Naharkatia"));
        put("Jharkhand", "Ranchi", List.of("Ranchi", "Bundu"));
        put("Jharkhand", "East Singhbhum", List.of("Jamshedpur", "Ghatsila"));
        put("Chhattisgarh", "Raipur", List.of("Raipur", "Abhanpur"));
        put("Chhattisgarh", "Durg", List.of("Bhilai", "Durg"));
        put("Uttarakhand", "Dehradun", List.of("Dehradun", "Rishikesh"));
        put("Uttarakhand", "Nainital", List.of("Haldwani", "Nainital"));
        put("Himachal Pradesh", "Shimla", List.of("Shimla", "Theog"));
        put("Himachal Pradesh", "Kangra", List.of("Dharamshala", "Palampur"));
        put("Goa", "North Goa", List.of("Panaji", "Mapusa"));
        put("Goa", "South Goa", List.of("Margao", "Vasco"));
        put("Jammu and Kashmir", "Srinagar", List.of("Srinagar", "Ganderbal"));
        put("Jammu and Kashmir", "Jammu", List.of("Jammu", "Akhnoor"));
        put("Ladakh", "Leh", List.of("Leh", "Kharu"));
        put("Ladakh", "Kargil", List.of("Kargil", "Drass"));
        put("Puducherry", "Puducherry", List.of("Puducherry", "Oulgaret"));
        put("Puducherry", "Karaikal", List.of("Karaikal", "Nedungadu"));
        put("Chandigarh", "Chandigarh", List.of("Sector 17", "Sector 22", "Manimajra"));
        put("Andaman and Nicobar Islands", "South Andaman", List.of("Port Blair", "Ferrargunj"));
        put("Andaman and Nicobar Islands", "North and Middle Andaman", List.of("Mayabunder", "Diglipur"));
        put("Dadra and Nagar Haveli and Daman and Diu", "Daman", List.of("Daman", "Moti Daman"));
        put("Dadra and Nagar Haveli and Daman and Diu", "Dadra and Nagar Haveli", List.of("Silvassa", "Naroli"));
        put("Lakshadweep", "Lakshadweep", List.of("Kavaratti", "Agatti"));
        put("Manipur", "Imphal West", List.of("Imphal", "Lamphelpat"));
        put("Manipur", "Imphal East", List.of("Porompat", "Andro"));
        put("Meghalaya", "East Khasi Hills", List.of("Shillong", "Sohra"));
        put("Meghalaya", "West Garo Hills", List.of("Tura", "Dadenggre"));
        put("Mizoram", "Aizawl", List.of("Aizawl", "Sairang"));
        put("Mizoram", "Lunglei", List.of("Lunglei", "Hnahthial"));
        put("Nagaland", "Kohima", List.of("Kohima", "Tseminyu"));
        put("Nagaland", "Dimapur", List.of("Dimapur", "Chumukedima"));
        put("Sikkim", "Gangtok", List.of("Gangtok", "Rangpo"));
        put("Sikkim", "Namchi", List.of("Namchi", "Jorethang"));
        put("Tripura", "West Tripura", List.of("Agartala", "Mohanpur"));
        put("Tripura", "South Tripura", List.of("Belonia", "Santirbazar"));
        put("Arunachal Pradesh", "Papum Pare", List.of("Itanagar", "Naharlagun"));
        put("Arunachal Pradesh", "West Kameng", List.of("Bomdila", "Rupa"));

        // Ensure every state has at least several districts (never only Headquarters)
        for (String state : STATES) {
            Map<String, List<String>> districts = tree.computeIfAbsent(state, k -> new LinkedHashMap<>());
            if (districts.isEmpty() || (districts.size() == 1 && districts.containsKey("Headquarters"))) {
                districts.clear();
                districts.put(state + " Central", List.of(state + " City", "Civil Lines"));
                districts.put(state + " North", List.of("North Town", "Industrial Area"));
                districts.put(state + " South", List.of("South Town", "Market Area"));
                districts.put(state + " East", List.of("East Colony", "Railway Colony"));
            }
        }
    }

    private void put(String state, String district, List<String> cities) {
        tree.computeIfAbsent(state, k -> new LinkedHashMap<>()).put(district, cities);
    }

    public List<String> states() {
        return STATES;
    }

    public List<String> districts(String state) {
        Map<String, List<String>> districts = tree.get(state);
        if (districts == null) {
            return List.of();
        }
        return new ArrayList<>(districts.keySet());
    }

    public List<String> cities(String state, String district) {
        Map<String, List<String>> districts = tree.get(state);
        if (districts == null) {
            return List.of();
        }
        return districts.getOrDefault(district, List.of());
    }
}
