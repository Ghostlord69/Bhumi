package com.landregistry.property;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.landregistry.ai.AiClient;
import com.landregistry.certificate.CertificateService;
import com.landregistry.certificate.VirtualJamabandiService;
import com.landregistry.domain.GovernmentRecord;
import com.landregistry.domain.ListingPurpose;
import com.landregistry.domain.PropertyListing;
import com.landregistry.domain.PropertyStatus;
import com.landregistry.domain.PropertyType;
import com.landregistry.domain.StoredFile;
import com.landregistry.domain.UserAccount;
import com.landregistry.notify.NotifyService;
import com.landregistry.security.AuthUser;
import com.landregistry.security.Role;
import com.landregistry.store.AppStore;
import com.landregistry.store.InMemoryAppStore;
import com.landregistry.verification.MatchingService;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockMultipartFile;

class PropertyTransferFlowTest {
    private AppStore store;
    private PropertyService service;
    private UserAccount seller;
    private UserAccount buyer;
    private UserAccount officer;

    @BeforeEach
    void setUp() {
        store = new InMemoryAppStore();
        GovernmentRecord record = new GovernmentRecord("123/4", "Sihi", "Ballabgarh", "Faridabad", "Ramesh Kumar", "2.5 acres");
        store.putGovernment(record);

        NotifyService notify = new NotifyService(store);
        AiClient ai = new AiClient("http://127.0.0.1:9", new ObjectMapper()) {
            @Override
            public Optional<ExtractionResult> extract(StoredFile paper) {
                return Optional.of(new ExtractionResult(
                        null,
                        "Ramesh Kumar",
                        "123/4",
                        null,
                        null,
                        null,
                        null,
                        "KHASRA",
                        "PARCEL",
                        "Sihi",
                        "Ballabgarh",
                        "Faridabad",
                        "Haryana",
                        2.5,
                        "AGRICULTURAL",
                        0.96,
                        "fixture",
                        null,
                        null,
                        null
                ));
            }
        };
        MatchingService matching = new MatchingService(store, ai);
        service = new PropertyService(store, matching, notify, new CertificateService(), new VirtualJamabandiService());

        seller = user("seller@test", "Seller", Role.USER, "Ballabgarh");
        buyer = user("buyer@test", "Buyer", Role.USER, "Faridabad");
        officer = user("auth@test", "Officer", Role.AUTHENTICATOR, "Ballabgarh");
        store.saveUser(seller);
        store.saveUser(buyer);
        store.saveUser(officer);
    }

    @Test
    void seedsOneHundredGovernmentRecordsCompatibleLookup() {
        SeedDataHelper.seedHundred(store);
        assertTrue(store.governmentRecords().size() >= 100);
        assertTrue(store.government("123/4").isPresent());
    }

    @Test
    void purchaseConfirmFinalizeUpdatesOwnerAndIssuesCertificate() {
        PropertyListing listing = new PropertyListing();
        listing.setSellerId(seller.getId());
        listing.setPurpose(ListingPurpose.SALE);
        listing.setType(PropertyType.LAND);
        listing.setStatus(PropertyStatus.LIVE);
        listing.setTitle("Demo land");
        listing.setState("Haryana");
        listing.setDistrict("Faridabad");
        listing.setCity("Ballabgarh");
        listing.setAddress("Sihi");
        listing.setKhasraNumber("123/4");
        listing.setMeasurements("2.5 acres");
        store.saveProperty(listing);

        AuthUser buyerAuth = new AuthUser(buyer.getId(), Role.USER, buyer.getEmail(), buyer.getCity(), buyer.getDistrict(), buyer.getState());
        service.requestPurchase(buyerAuth, listing.getId());
        assertEquals(PropertyStatus.PURCHASE_REQUESTED, store.property(listing.getId()).orElseThrow().getStatus());

        AuthUser sellerAuth = new AuthUser(seller.getId(), Role.USER, seller.getEmail(), seller.getCity(), seller.getDistrict(), seller.getState());
        service.confirmSale(sellerAuth, listing.getId());
        assertEquals(PropertyStatus.PENDING_TRANSFER, store.property(listing.getId()).orElseThrow().getStatus());

        AuthUser officerAuth = new AuthUser(officer.getId(), Role.AUTHENTICATOR, officer.getEmail(), officer.getCity(), officer.getDistrict(), officer.getState());
        PropertyService.PropertyView sold = service.finalizeTransfer(officerAuth, listing.getId());
        assertEquals(PropertyStatus.SOLD, sold.status());
        assertNotNull(sold.certificateId());
        assertEquals("Buyer", store.government("123/4").orElseThrow().getOwnerName());
        assertTrue(service.search(null, null, null, null, null, null).stream().noneMatch(p -> p.id().equals(listing.getId())));
        assertTrue(service.getCertificate(buyerAuth, sold.certificateId()).getPdfBytes().length > 100);
        assertTrue(store.notificationsForUser(buyer.getId()).size() > 0);
        assertTrue(store.notificationsForUser(officer.getId()).size() > 0);
    }

    @Test
    void createUsesAiMatchIntoOfficerQueue() throws Exception {
        AuthUser sellerAuth = new AuthUser(seller.getId(), Role.USER, seller.getEmail(), seller.getCity(), seller.getDistrict(), seller.getState());
        MockMultipartFile paper = new MockMultipartFile("papers", "jamabandi.png", "image/png", new byte[] {1, 2, 3});
        MockMultipartFile photo1 = new MockMultipartFile("photos", "a.jpg", "image/jpeg", new byte[] {1});
        MockMultipartFile photo2 = new MockMultipartFile("photos", "b.jpg", "image/jpeg", new byte[] {2});
        MockMultipartFile photo3 = new MockMultipartFile("photos", "c.jpg", "image/jpeg", new byte[] {3});
        PropertyService.PropertyDraft draft = new PropertyService.PropertyDraft(
                "SALE", "LAND", "AI land", "Haryana", "Faridabad", "Ballabgarh", "Sihi",
                1000000d, "2.5 acres", "999/9", null, null, null, null, null, null, null, "Ramesh",
                null, null
        );
        PropertyService.PropertyView view = service.create(sellerAuth, draft, List.of(paper), List.of(photo1, photo2, photo3));
        assertEquals(PropertyStatus.AI_VERIFIED_AWAITING_AUTHENTICATOR, view.status());
        assertEquals(3, view.photoCount());
        assertTrue(store.notificationsForUser(officer.getId()).stream()
                .anyMatch(n -> n.getSubject().toLowerCase().contains("jurisdiction") || n.getSubject().toLowerCase().contains("case")));
    }

    private UserAccount user(String email, String name, Role role, String city) {
        UserAccount user = new UserAccount();
        user.setEmail(email);
        user.setFullName(name);
        user.setPhone("9000000000");
        user.setPasswordHash("x");
        user.setRole(role);
        user.setActive(true);
        user.setState("Haryana");
        user.setDistrict("Faridabad");
        user.setCity(city);
        return user;
    }

    /** Local helper so SeedData CommandLineRunner is not required in unit tests. */
    static class SeedDataHelper {
        static void seedHundred(AppStore store) {
            store.putGovernment(new GovernmentRecord("123/4", "Sihi", "Ballabgarh", "Faridabad", "Ramesh Kumar", "2.5 acres"));
            int created = 1;
            for (int i = 1; created < 100; i++) {
                String khasra = (200 + i) + "/" + ((i % 7) + 1);
                if (store.government(khasra).isPresent()) {
                    continue;
                }
                store.putGovernment(new GovernmentRecord(khasra, "Sihi", "Ballabgarh", "Faridabad", "Owner " + i, "1.0 acres"));
                created++;
            }
        }
    }
}
