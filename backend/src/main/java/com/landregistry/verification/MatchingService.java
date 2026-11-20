package com.landregistry.verification;

import com.landregistry.ai.AiClient;
import com.landregistry.domain.GovernmentRecord;
import com.landregistry.domain.ListingPurpose;
import com.landregistry.domain.PropertyListing;
import com.landregistry.domain.PropertyStatus;
import com.landregistry.domain.StoredFile;
import com.landregistry.domain.UserAccount;
import com.landregistry.store.AppStore;
import java.util.Locale;
import java.util.Optional;
import org.springframework.stereotype.Service;

@Service
public class MatchingService {
    private final AppStore store;
    private final AiClient aiClient;

    public MatchingService(AppStore store, AiClient aiClient) {
        this.store = store;
        this.aiClient = aiClient;
    }

    public void run(PropertyListing listing, UserAccount seller) {
        if (listing.getPurpose() == ListingPurpose.REGISTRY) {
            listing.setStatus(PropertyStatus.PENDING_REGISTRY);
            listing.setAiSummary(
                    "Registry request. Applicant: " + seller.getFullName()
                            + ", email " + seller.getEmail()
                            + ", phone " + seller.getPhone()
                            + ". Authenticator should complete new registration for this plot.");
            return;
        }

        Optional<AiClient.ExtractionResult> extractionOpt = Optional.empty();
        if (!listing.getRegistryPapers().isEmpty()) {
            StoredFile paper = listing.getRegistryPapers().get(0);
            extractionOpt = aiClient.extract(paper);
        }
        final Optional<AiClient.ExtractionResult> extraction = extractionOpt;

        extraction.ifPresent(result -> applyExtractionToListing(listing, result));
        // Form-entered ULPIN wins if AI missed it
        if ((listing.getUlpin() == null || listing.getUlpin().isBlank()) && extraction.isPresent()
                && extraction.get().ulpin() != null) {
            listing.setUlpin(extraction.get().ulpin());
        }

        Optional<GovernmentRecord> recordOpt = resolveGovernmentRecord(listing, extraction.orElse(null));
        if (recordOpt.isEmpty()) {
            listing.setStatus(PropertyStatus.NEEDS_PHYSICAL_VERIFICATION);
            String tier = extraction.map(AiClient.ExtractionResult::matchTier).orElse("NONE");
            String aiBit = extraction.map(r -> " Match tier " + tier + ".")
                    .orElse(" AI unavailable; using form identifiers.");
            String idHint = identifierHint(listing);
            listing.setAiSummary("No matching government record found for " + idHint + "."
                    + aiBit + " Physical verification is required.");
            return;
        }
        applyMatch(listing, recordOpt.get(), extraction.orElse(null));
    }

    private void applyExtractionToListing(PropertyListing listing, AiClient.ExtractionResult result) {
        if (result.ulpin() != null && !result.ulpin().isBlank()) {
            listing.setUlpin(result.ulpin().toUpperCase(Locale.ROOT));
        }
        if (result.khasraNumber() != null && !result.khasraNumber().isBlank()) {
            listing.setKhasraNumber(result.khasraNumber());
        }
        if (result.surveyNumber() != null && !result.surveyNumber().isBlank()) {
            listing.setSurveyNumber(result.surveyNumber());
            if (listing.getKhasraNumber() == null || listing.getKhasraNumber().isBlank()) {
                // South-India survey acts as parcel key for listing display / transfer flows
                listing.setKhasraNumber(result.surveyNumber());
            }
        }
        if (result.khataNumber() != null && !result.khataNumber().isBlank()) {
            listing.setKhataNumber(result.khataNumber());
        }
        if (result.khewatNumber() != null && !result.khewatNumber().isBlank()) {
            listing.setKhewatNumber(result.khewatNumber());
        }
        if (result.khatauniNumber() != null && !result.khatauniNumber().isBlank()) {
            listing.setKhatauniNumber(result.khatauniNumber());
        }
        if ((listing.getMeasurements() == null || listing.getMeasurements().isBlank())
                && result.areaAcres() != null) {
            listing.setMeasurements(result.areaAcres() + " acres");
        }
        if (result.ownerName() != null && (listing.getExtraNotes() == null || listing.getExtraNotes().isBlank())) {
            listing.setExtraNotes("Owner on paper: " + result.ownerName());
        }
        if (result.latitude() != null && result.longitude() != null) {
            listing.setLatitude(result.latitude());
            listing.setLongitude(result.longitude());
        } else if (listing.getUlpin() != null && !listing.getUlpin().isBlank()) {
            double[] decoded = com.landregistry.location.UlpinCodec.decode(listing.getUlpin());
            if (decoded != null) {
                listing.setLatitude(decoded[0]);
                listing.setLongitude(decoded[1]);
            }
        }
    }

    private Optional<GovernmentRecord> resolveGovernmentRecord(
            PropertyListing listing, AiClient.ExtractionResult extraction) {
        if (extraction != null && extraction.ulpin() != null && !extraction.ulpin().isBlank()) {
            Optional<GovernmentRecord> byUlpin = store.governmentByUlpin(extraction.ulpin());
            if (byUlpin.isPresent()) {
                return byUlpin;
            }
        }
        if (listing.getUlpin() != null && !listing.getUlpin().isBlank()) {
            Optional<GovernmentRecord> byUlpin = store.governmentByUlpin(listing.getUlpin());
            if (byUlpin.isPresent()) {
                return byUlpin;
            }
        }

        String khasra = listing.getKhasraNumber();
        if (khasra != null && !khasra.isBlank()) {
            Optional<GovernmentRecord> byKhasra = store.government(khasra);
            if (byKhasra.isPresent()) {
                return byKhasra;
            }
        }

        String survey = listing.getSurveyNumber();
        if (survey == null && extraction != null) {
            survey = extraction.surveyNumber();
        }
        if (survey != null && !survey.isBlank()) {
            return store.governmentBySurvey(survey);
        }
        return Optional.empty();
    }

    private String identifierHint(PropertyListing listing) {
        if (listing.getUlpin() != null && !listing.getUlpin().isBlank()) {
            return "ULPIN " + listing.getUlpin();
        }
        if (listing.getKhasraNumber() != null && !listing.getKhasraNumber().isBlank()) {
            return "khasra/survey " + listing.getKhasraNumber();
        }
        if (listing.getSurveyNumber() != null && !listing.getSurveyNumber().isBlank()) {
            return "survey " + listing.getSurveyNumber();
        }
        return "extracted land identifiers";
    }

    private void applyMatch(PropertyListing listing, GovernmentRecord record, AiClient.ExtractionResult extraction) {
        // ULPIN is sufficient identity when present and confident
        boolean ulpinMatch = extraction != null
                && extraction.ulpin() != null
                && !extraction.ulpin().isBlank()
                && record.getUlpin() != null
                && extraction.ulpin().equalsIgnoreCase(record.getUlpin());

        boolean cityOk = record.getCity().equalsIgnoreCase(listing.getCity());
        if (extraction != null && extraction.tehsil() != null) {
            cityOk = cityOk || record.getCity().equalsIgnoreCase(extraction.tehsil());
        }

        String ownerHintSource = listing.getExtraNotes();
        if (extraction != null && extraction.ownerName() != null) {
            ownerHintSource = extraction.ownerName();
        }
        boolean ownerOk = ownerHintSource == null || ownerHintSource.isBlank()
                || ownerHintSource.toLowerCase(Locale.ROOT)
                .contains(record.getOwnerName().split(" ")[0].toLowerCase(Locale.ROOT));

        // Khata / khewat corroborate ownership when both sides have them
        boolean ownershipIdOk = true;
        if (extraction != null) {
            if (extraction.khataNumber() != null && record.getKhataNumber() != null
                    && !record.getKhataNumber().isBlank()) {
                ownershipIdOk = ownershipIdOk
                        && extraction.khataNumber().equalsIgnoreCase(record.getKhataNumber());
            }
            if (extraction.khewatNumber() != null && record.getKhewatNumber() != null
                    && !record.getKhewatNumber().isBlank()) {
                ownershipIdOk = ownershipIdOk
                        && extraction.khewatNumber().equalsIgnoreCase(record.getKhewatNumber());
            }
        }

        boolean highConfidence = extraction == null || extraction.confidence() >= 0.75;
        boolean parcelExact = extraction == null
                || extraction.khasraNumber() == null
                || record.getKhasraNumber() == null
                || extraction.khasraNumber().equalsIgnoreCase(record.getKhasraNumber())
                || (extraction.surveyNumber() != null && record.getSurveyNumber() != null
                && extraction.surveyNumber().equalsIgnoreCase(record.getSurveyNumber()));

        boolean matched;
        if (ulpinMatch && highConfidence) {
            matched = true;
        } else {
            matched = cityOk && ownerOk && ownershipIdOk && highConfidence && parcelExact;
        }

        if (matched) {
            listing.setStatus(PropertyStatus.AI_VERIFIED_AWAITING_AUTHENTICATOR);
            if (listing.getKhasraNumber() == null || listing.getKhasraNumber().isBlank()) {
                listing.setKhasraNumber(record.getKhasraNumber());
            }
            if (listing.getUlpin() == null || listing.getUlpin().isBlank()) {
                listing.setUlpin(record.getUlpin());
            }
            String idPart = ulpinMatch
                    ? "ULPIN " + record.getUlpin()
                    : "khasra " + record.getKhasraNumber();
            listing.setAiSummary("AI matched government record: " + idPart
                    + ", owner " + record.getOwnerName()
                    + ", " + record.getMeasurements()
                    + (extraction != null ? " (tier " + nullSafe(extraction.matchTier()) + ")" : "")
                    + ". Waiting for Patwari/Tehsildar final approval.");
            if (listing.getMeasurements() == null || listing.getMeasurements().isBlank()) {
                listing.setMeasurements(record.getMeasurements());
            }
        } else {
            listing.setStatus(PropertyStatus.NEEDS_PHYSICAL_VERIFICATION);
            listing.setAiSummary("Record found but AI/city/owner/land-id details did not fully align"
                    + (extraction != null ? " (tier " + nullSafe(extraction.matchTier()) + ")" : "")
                    + ". Physical verification required.");
        }
    }

    private static String nullSafe(String value) {
        return value == null ? "UNKNOWN" : value;
    }
}
