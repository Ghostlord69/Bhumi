package com.landregistry.store;

import com.landregistry.domain.GovernmentRecord;
import com.landregistry.domain.ListingPurpose;
import com.landregistry.domain.PropertyListing;
import com.landregistry.domain.PropertyStatus;
import com.landregistry.domain.PropertyType;
import com.landregistry.domain.StateAdmin;
import com.landregistry.domain.StoredFile;
import com.landregistry.domain.UserAccount;
import com.landregistry.location.StateCodes;
import com.landregistry.security.Role;
import java.io.IOException;
import java.io.InputStream;
import java.util.Map;
import java.util.UUID;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.io.ClassPathResource;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class SeedData implements CommandLineRunner {
    private static final String[] FIRST_NAMES = {
            "Ramesh", "Anita", "Suresh", "Priya", "Vikram", "Sunita", "Amit", "Neha", "Rajesh", "Kavita",
            "Manoj", "Pooja", "Deepak", "Meena", "Sanjay", "Rekha", "Anil", "Geeta", "Naveen", "Shweta"
    };
    private static final String[] LAST_NAMES = {
            "Kumar", "Sharma", "Singh", "Verma", "Yadav", "Gupta", "Malik", "Chauhan", "Ahlawat", "Tanwar"
    };
    private static final String[] VILLAGES = {
            "Sihi", "Palla", "Dayalpur", "Chhainsa", "Tigaon", "Uncha Gaon", "Sohna Road Ext", "Sector Approach",
            "Lalpur", "Jasana", "Bhankri", "Kheri Kalan", "Badrola", "Fatehpur Biloch", "Mawai"
    };
    private static final String[] CITIES = {"Ballabgarh", "Faridabad", "Greater Faridabad"};
    private static final String[] MEASUREMENTS = {
            "1.0 acres", "1.5 acres", "2.0 acres", "2.5 acres", "3.0 acres",
            "800 sq. yd.", "1,200 sq. yd.", "1,800 sq. yd.", "2,200 sq. yd.", "450 sq. yd."
    };

    private final AppStore store;
    private final PasswordEncoder encoder;

    public SeedData(AppStore store, PasswordEncoder encoder) {
        this.store = store;
        this.encoder = encoder;
    }

    @Override
    public void run(String... args) {
        if (store.userCount() > 0) {
            return;
        }
        seedGovernmentRecords();
        seedStateAdmins();

        UserAccount officer = user("auth.ballabgarh@bhumi.gov.in", "Auth@123", "Patwari Ballabgarh",
                "9999990002", Role.AUTHENTICATOR, "Haryana", "Faridabad", "Ballabgarh", true);
        officer.setOfficialLogin("auth.ballabgarh@bhumi.gov.in");
        store.saveUser(officer);

        UserAccount demoUser = user("user@bhumi.test", "User@123", "Meera Singh",
                "9876543210", Role.USER, "Haryana", "Faridabad", "Ballabgarh", true);
        store.saveUser(demoUser);

        store.saveProperty(live(demoUser.getId(), "Agricultural land near Sihi", "Haryana", "Faridabad", "Ballabgarh",
                "Khasra approach road, Sihi village", 3500000d, "2.5 acres", PropertyType.LAND,
                "land-1", "land-2", "land-4"));
        store.saveProperty(live(demoUser.getId(), "Independent house, Sector 2", "Haryana", "Faridabad", "Ballabgarh",
                "House 14, Sector 2, Ballabgarh", 8900000d, "180 sq. yd. plot, 3 BHK", PropertyType.HOUSE,
                "house-1", "house-5", "flat-3"));
        store.saveProperty(live(demoUser.getId(), "NIT Faridabad 2 BHK", "Haryana", "Faridabad", "Faridabad",
                "Flat 12B, Green Residency, NIT", 6200000d, "1,050 sq. ft.", PropertyType.FLAT,
                "flat-5", "flat-2", "flat-4"));

        UserAccount seller = user("seller@bhumi.test", "Seller@123", "Rajesh Verma",
                "9876543211", Role.USER, "Haryana", "Gurugram", "Gurugram", true);
        store.saveUser(seller);
        seedMarketplace(seller.getId());
    }

    private void seedMarketplace(Long sellerId) {
        store.saveProperty(live(sellerId, "Mustard farmland with boundary stones", "Haryana", "Faridabad", "Greater Faridabad",
                "Village Tigaon, Greater Faridabad", 4800000d, "3.0 acres", PropertyType.LAND,
                "land-4", "land-1", "land-2"));
        store.saveProperty(live(sellerId, "Fenced farm with tubewell", "Haryana", "Karnal", "Karnal",
                "Kunjpura Road, Karnal", 6500000d, "4.0 acres", PropertyType.LAND,
                "land-2", "land-1", "land-4"));
        store.saveProperty(live(sellerId, "Residential plot in Sector 92", "Haryana", "Gurugram", "Gurugram",
                "Plot 47, Sector 92, New Gurugram", 21000000d, "300 sq. yd.", PropertyType.LAND,
                "land-3", "land-6", "land-1"));
        store.saveProperty(live(sellerId, "Mango orchard near Gomti", "Uttar Pradesh", "Lucknow", "Lucknow",
                "Malihabad Road, Lucknow", 9500000d, "5.5 acres", PropertyType.LAND,
                "land-5", "land-4", "land-2"));
        store.saveProperty(live(sellerId, "Highway-facing commercial plot", "Rajasthan", "Jaipur", "Sanganer",
                "NH-52 corner, Sanganer, Jaipur", 32000000d, "2,400 sq. yd.", PropertyType.LAND,
                "land-6", "land-3", "land-1"));
        store.saveProperty(live(sellerId, "Modern 4 BHK kothi in Sector 15", "Haryana", "Faridabad", "Faridabad",
                "House 221, Sector 15, Faridabad", 28500000d, "300 sq. yd. plot, 4 BHK", PropertyType.HOUSE,
                "house-1", "house-5", "flat-3"));
        store.saveProperty(live(sellerId, "Garden villa in Whitefield", "Karnataka", "Bengaluru Urban", "Whitefield",
                "Palm Meadows, Whitefield, Bengaluru", 42000000d, "3,600 sq. ft., 4 BHK", PropertyType.HOUSE,
                "house-2", "house-5", "flat-4"));
        store.saveProperty(live(sellerId, "Heritage haveli in Pink City", "Rajasthan", "Jaipur", "Jaipur",
                "Chandpole Bazaar lane, Jaipur", 36000000d, "5,200 sq. ft., 6 BHK", PropertyType.HOUSE,
                "house-3", "house-5", "land-6"));
        store.saveProperty(live(sellerId, "Duplex row house, Hinjewadi", "Maharashtra", "Pune", "Hinjewadi",
                "Phase 2, Hinjewadi, Pune", 17500000d, "2,100 sq. ft., 3 BHK", PropertyType.HOUSE,
                "house-4", "house-5", "flat-3"));
        store.saveProperty(live(sellerId, "Three-storey family home, Gomti Nagar", "Uttar Pradesh", "Lucknow", "Gomti Nagar",
                "Vipul Khand 3, Gomti Nagar", 24000000d, "2,700 sq. ft., 5 BHK", PropertyType.HOUSE,
                "house-6", "house-5", "flat-4"));
        store.saveProperty(live(sellerId, "3 BHK with pool view, Sector 150", "Uttar Pradesh", "Gautam Buddha Nagar", "Noida",
                "Tower C, Sector 150, Noida", 13500000d, "1,650 sq. ft.", PropertyType.FLAT,
                "flat-1", "flat-2", "flat-3"));
        store.saveProperty(live(sellerId, "Skyline 2 BHK on Golf Course Road", "Haryana", "Gurugram", "Gurugram",
                "Golf Course Road, Sector 54, Gurugram", 19800000d, "1,380 sq. ft.", PropertyType.FLAT,
                "flat-6", "flat-4", "flat-2"));
        store.saveProperty(live(sellerId, "Andheri West 2 BHK near metro", "Maharashtra", "Mumbai Suburban", "Andheri",
                "Lokhandwala Complex, Andheri West", 26500000d, "980 sq. ft.", PropertyType.FLAT,
                "flat-5", "flat-3", "flat-4"));
        store.saveProperty(live(sellerId, "Furnished 3 BHK, Electronic City", "Karnataka", "Bengaluru Urban", "Electronic City",
                "Phase 1, Electronic City, Bengaluru", 9800000d, "1,420 sq. ft.", PropertyType.FLAT,
                "flat-2", "flat-4", "flat-3"));
        store.saveProperty(live(sellerId, "Greater Faridabad 3 BHK, Sector 85", "Haryana", "Faridabad", "Greater Faridabad",
                "Tower B, Sector 85, Greater Faridabad", 8400000d, "1,550 sq. ft.", PropertyType.FLAT,
                "flat-1", "flat-6", "flat-2"));
    }

    private void seedStateAdmins() {
        int phone = 910000000;
        for (Map.Entry<String, String> entry : StateCodes.all().entrySet()) {
            String state = entry.getKey();
            String code = entry.getValue();
            String email = StateCodes.adminEmail(code);
            String password = StateCodes.adminPassword(code);
            UserAccount admin = user(email, password, state + " State Admin",
                    String.valueOf(phone++), Role.ADMIN, state, "Headquarters", "City Centre", true);
            admin.setOfficialLogin(email);
            store.saveUser(admin);
            store.saveStateAdmin(stateAdmin(admin, state));
        }
    }

    private StateAdmin stateAdmin(UserAccount user, String state) {
        StateAdmin admin = new StateAdmin();
        admin.setUserId(user.getId());
        admin.setStateUnionTerritory(state);
        admin.setEmail(user.getEmail());
        admin.setPhone(user.getPhone());
        admin.setFullName(user.getFullName());
        admin.setActive(true);
        return admin;
    }

    private void seedGovernmentRecords() {
        GovernmentRecord golden = new GovernmentRecord("123/4", "Sihi", "Ballabgarh", "Faridabad", "Ramesh Kumar", "2.5 acres");
        golden.setUlpin("HR06A1B2C3D4E5");
        golden.setKhataNumber("45");
        golden.setKhewatNumber("12");
        golden.setKhatauniNumber("3");
        golden.setOwnerPhone("9876500001");
        store.putGovernment(golden);

        GovernmentRecord second = new GovernmentRecord("88/1", "Palla", "Ballabgarh", "Faridabad", "Anita Sharma", "1,800 sq. yd.");
        second.setKhataNumber("22");
        second.setKhewatNumber("8");
        second.setOwnerPhone("9876500002");
        store.putGovernment(second);

        GovernmentRecord ulpinOnly = new GovernmentRecord("999/1", "Sihi", "Ballabgarh", "Faridabad", "Demo Ulpin Owner", "1.2 acres");
        ulpinOnly.setUlpin("HR06F6G7H8I9J0");
        ulpinOnly.setOwnerPhone("9876500003");
        store.putGovernment(ulpinOnly);

        GovernmentRecord survey = new GovernmentRecord("201/3", "Anantapur Rural", "Anantapur", "Anantapur", "Lakshmi Reddy", "3.0 acres");
        survey.setSurveyNumber("201/3");
        survey.setKhataNumber("88");
        survey.setOwnerPhone("9876500004");
        store.putGovernment(survey);

        int created = 4;
        for (int i = 1; created < 100; i++) {
            String khasra = (200 + i) + "/" + ((i % 17) + 1);
            if (store.government(khasra).isPresent()) {
                continue;
            }
            String city = CITIES[i % CITIES.length];
            String village = VILLAGES[i % VILLAGES.length];
            String owner = FIRST_NAMES[i % FIRST_NAMES.length] + " " + LAST_NAMES[(i * 3) % LAST_NAMES.length];
            String measurements = MEASUREMENTS[i % MEASUREMENTS.length];
            GovernmentRecord record = new GovernmentRecord(khasra, village, city, "Faridabad", owner, measurements);
            record.setOwnerPhone(String.format("98%08d", 70000000 + i));
            store.putGovernment(record);
            created++;
        }
    }

    private UserAccount user(String email, String password, String name, String phone, Role role,
                             String state, String district, String city, boolean active) {
        UserAccount user = new UserAccount();
        user.setEmail(email);
        user.setPasswordHash(encoder.encode(password));
        user.setFullName(name);
        user.setPhone(phone);
        user.setRole(role);
        user.setState(state);
        user.setDistrict(district);
        user.setCity(city);
        user.setActive(active);
        return user;
    }

    private PropertyListing live(Long sellerId, String title, String state, String district, String city,
                                 String address, double price, String measurements, PropertyType type,
                                 String... photos) {
        PropertyListing listing = new PropertyListing();
        listing.setSellerId(sellerId);
        listing.setPurpose(ListingPurpose.SALE);
        listing.setType(type);
        listing.setStatus(PropertyStatus.LIVE);
        listing.setTitle(title);
        listing.setState(state);
        listing.setDistrict(district);
        listing.setCity(city);
        listing.setAddress(address);
        listing.setAskingPrice(price);
        listing.setMeasurements(measurements);
        listing.setFurnished(type != PropertyType.LAND);
        listing.setBedrooms(type == PropertyType.LAND ? null : 3);
        for (String photo : photos) {
            StoredFile file = seedPhoto(photo);
            if (file != null) {
                listing.getPropertyPhotos().add(file);
            }
        }
        return listing;
    }

    /** Loads a bundled demo photo from {@code classpath:seed-photos/<name>.jpg}; null if missing. */
    private StoredFile seedPhoto(String name) {
        try (InputStream in = new ClassPathResource("seed-photos/" + name + ".jpg").getInputStream()) {
            StoredFile file = new StoredFile();
            file.setId(UUID.randomUUID().toString());
            file.setOriginalName(name + ".jpg");
            file.setContentType("image/jpeg");
            file.setBytes(in.readAllBytes());
            return file;
        } catch (IOException e) {
            return null;
        }
    }
}
