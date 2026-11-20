package com.landregistry.verification;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.landregistry.ai.AiClient;
import com.landregistry.domain.GovernmentRecord;
import com.landregistry.domain.ListingPurpose;
import com.landregistry.domain.PropertyListing;
import com.landregistry.domain.PropertyStatus;
import com.landregistry.domain.PropertyType;
import com.landregistry.domain.StoredFile;
import com.landregistry.domain.UserAccount;
import com.landregistry.store.InMemoryAppStore;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class MatchingServiceUlpinTest {
    private InMemoryAppStore store;
    private AiClient aiClient;
    private MatchingService matchingService;

    @BeforeEach
    void setUp() {
        store = new InMemoryAppStore();
        aiClient = mock(AiClient.class);
        matchingService = new MatchingService(store, aiClient);

        GovernmentRecord withUlpin = new GovernmentRecord(
                "999/1", "Sihi", "Ballabgarh", "Faridabad", "Demo Ulpin Owner", "1.2 acres");
        withUlpin.setUlpin("HR06F6G7H8I9J0");
        store.putGovernment(withUlpin);

        GovernmentRecord khasra = new GovernmentRecord(
                "123/4", "Sihi", "Ballabgarh", "Faridabad", "Ramesh Kumar", "2.5 acres");
        khasra.setUlpin("HR06A1B2C3D4E5");
        khasra.setKhataNumber("45");
        store.putGovernment(khasra);

        GovernmentRecord survey = new GovernmentRecord(
                "201/3", "Anantapur Rural", "Anantapur", "Anantapur", "Lakshmi Reddy", "3.0 acres");
        survey.setSurveyNumber("201/3");
        store.putGovernment(survey);
    }

    @Test
    void matchesByUlpinWithoutRequiringFormKhasra() {
        when(aiClient.extract(any())).thenReturn(Optional.of(extraction(
                "HR06F6G7H8I9J0", null, null, null, null, "Demo Ulpin Owner", "Ballabgarh", 0.93, "ULPIN")));

        PropertyListing listing = baseListing();
        listing.setKhasraNumber(null);
        listing.getRegistryPapers().add(paper());

        matchingService.run(listing, seller());

        assertEquals(PropertyStatus.AI_VERIFIED_AWAITING_AUTHENTICATOR, listing.getStatus());
        assertEquals("HR06F6G7H8I9J0", listing.getUlpin());
        assertTrue(listing.getAiSummary().contains("ULPIN"));
    }

    @Test
    void matchesByKhasraWhenUlpinAbsent() {
        when(aiClient.extract(any())).thenReturn(Optional.of(extraction(
                null, "123/4", null, "45", null, "Ramesh Kumar", "Ballabgarh", 0.88, "PARCEL")));

        PropertyListing listing = baseListing();
        listing.setKhasraNumber("123/4");
        listing.getRegistryPapers().add(paper());

        matchingService.run(listing, seller());

        assertEquals(PropertyStatus.AI_VERIFIED_AWAITING_AUTHENTICATOR, listing.getStatus());
        assertTrue(listing.getAiSummary().contains("123/4"));
    }

    @Test
    void matchesBySurveyNumber() {
        when(aiClient.extract(any())).thenReturn(Optional.of(extraction(
                null, null, "201/3", null, null, "Lakshmi Reddy", "Anantapur", 0.86, "PARCEL")));

        PropertyListing listing = baseListing();
        listing.setCity("Anantapur");
        listing.setDistrict("Anantapur");
        listing.setKhasraNumber(null);
        listing.getRegistryPapers().add(paper());

        matchingService.run(listing, seller());

        assertEquals(PropertyStatus.AI_VERIFIED_AWAITING_AUTHENTICATOR, listing.getStatus());
        assertEquals("201/3", listing.getSurveyNumber());
    }

    @Test
    void lowConfidenceGoesToPhysicalVerification() {
        when(aiClient.extract(any())).thenReturn(Optional.of(extraction(
                "HR06F6G7H8I9J0", null, null, null, null, "Demo Ulpin Owner", "Ballabgarh", 0.40, "ULPIN")));

        PropertyListing listing = baseListing();
        listing.getRegistryPapers().add(paper());

        matchingService.run(listing, seller());

        assertEquals(PropertyStatus.NEEDS_PHYSICAL_VERIFICATION, listing.getStatus());
    }

    private static AiClient.ExtractionResult extraction(
            String ulpin,
            String khasra,
            String survey,
            String khata,
            String khewat,
            String owner,
            String tehsil,
            double confidence,
            String tier) {
        return new AiClient.ExtractionResult(
                ulpin,
                owner,
                khasra,
                survey,
                khata,
                khewat,
                null,
                ulpin != null ? "ULPIN" : (khasra != null ? "KHASRA" : "SURVEY"),
                tier,
                null,
                tehsil,
                null,
                null,
                null,
                "AGRICULTURAL",
                confidence,
                null,
                null,
                null,
                null);
    }

    private static PropertyListing baseListing() {
        PropertyListing listing = new PropertyListing();
        listing.setPurpose(ListingPurpose.SALE);
        listing.setType(PropertyType.LAND);
        listing.setTitle("Test land");
        listing.setState("Haryana");
        listing.setDistrict("Faridabad");
        listing.setCity("Ballabgarh");
        listing.setAddress("Sihi");
        listing.setStatus(PropertyStatus.PENDING_AI);
        return listing;
    }

    private static StoredFile paper() {
        StoredFile file = new StoredFile();
        file.setId("t1");
        file.setOriginalName("paper.png");
        file.setContentType("image/png");
        file.setBytes(new byte[] {1, 2, 3});
        return file;
    }

    private static UserAccount seller() {
        UserAccount user = new UserAccount();
        user.setId(1L);
        user.setFullName("Seller");
        user.setEmail("s@test");
        user.setPhone("1");
        return user;
    }
}
