package com.landregistry.property;

import com.landregistry.certificate.CertificateService;
import com.landregistry.certificate.VirtualJamabandiService;
import com.landregistry.common.ApiException;
import com.landregistry.domain.GovernmentRecord;
import com.landregistry.domain.ListingPurpose;
import com.landregistry.domain.PropertyListing;
import com.landregistry.domain.PropertyStatus;
import com.landregistry.domain.PropertyType;
import com.landregistry.domain.StoredFile;
import com.landregistry.domain.TransferCertificate;
import com.landregistry.domain.UserAccount;
import com.landregistry.location.GeoCentroids;
import com.landregistry.location.UlpinCodec;
import com.landregistry.notify.NotifyService;
import com.landregistry.security.AuthUser;
import com.landregistry.security.Role;
import com.landregistry.store.AppStore;
import com.landregistry.verification.MatchingService;
import java.time.Instant;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

@Service
public class PropertyService {
    private final AppStore store;
    private final MatchingService matchingService;
    private final NotifyService notifyService;
    private final CertificateService certificateService;
    private final VirtualJamabandiService virtualJamabandiService;

    public PropertyService(
            AppStore store,
            MatchingService matchingService,
            NotifyService notifyService,
            CertificateService certificateService,
            VirtualJamabandiService virtualJamabandiService
    ) {
        this.store = store;
        this.matchingService = matchingService;
        this.notifyService = notifyService;
        this.certificateService = certificateService;
        this.virtualJamabandiService = virtualJamabandiService;
    }

    public List<PropertyView> search(String type, String state, String district, String city, Double minPrice, Double maxPrice) {
        return store.properties().stream()
                .filter(p -> p.getStatus() == PropertyStatus.LIVE)
                .filter(p -> p.getPurpose() == ListingPurpose.SALE)
                .filter(p -> match(type, p.getType() == null ? null : p.getType().name()))
                .filter(p -> match(state, p.getState()))
                .filter(p -> match(district, p.getDistrict()))
                .filter(p -> match(city, p.getCity()))
                .filter(p -> minPrice == null || (p.getAskingPrice() != null && p.getAskingPrice() >= minPrice))
                .filter(p -> maxPrice == null || (p.getAskingPrice() != null && p.getAskingPrice() <= maxPrice))
                .map(p -> toView(p, false))
                .toList();
    }

    /** Prefer same city, then district, then state — for logged-in USER home without filters. */
    public List<PropertyView> recommended(String state, String district, String city) {
        return store.properties().stream()
                .filter(p -> p.getStatus() == PropertyStatus.LIVE)
                .filter(p -> p.getPurpose() == ListingPurpose.SALE)
                .sorted(Comparator
                        .comparingInt((PropertyListing p) -> recommendRank(p, state, district, city))
                        .thenComparing(PropertyListing::getCreatedAt, Comparator.nullsLast(Comparator.reverseOrder())))
                .filter(p -> recommendRank(p, state, district, city) < 3)
                .map(p -> toView(p, false))
                .toList();
    }

    private int recommendRank(PropertyListing p, String state, String district, String city) {
        if (city != null && !city.isBlank() && city.equalsIgnoreCase(p.getCity())) return 0;
        if (district != null && !district.isBlank() && district.equalsIgnoreCase(p.getDistrict())) return 1;
        if (state != null && !state.isBlank() && state.equalsIgnoreCase(p.getState())) return 2;
        return 3;
    }

    public PropertyView publicDetail(Long id) {
        PropertyListing listing = store.property(id).orElseThrow(() -> new ApiException(404, "Property not found"));
        if (listing.getStatus() != PropertyStatus.LIVE || listing.getPurpose() != ListingPurpose.SALE) {
            throw new ApiException(404, "Property not found");
        }
        return toView(listing, false);
    }

    public PropertyView create(AuthUser actor, PropertyDraft draft, List<MultipartFile> papers, List<MultipartFile> photos) {
        if (actor.role() != Role.USER) {
            throw new ApiException(403, "Sign in as a user to post property");
        }
        if (papers == null || papers.isEmpty()) {
            throw new ApiException(400, "Registry papers are mandatory");
        }
        if (draft.purpose() != null && "SALE".equalsIgnoreCase(draft.purpose())
                && (photos == null || photos.size() < 3)) {
            throw new ApiException(400, "At least 3 property photos are required for sale listings");
        }
        UserAccount seller = store.user(actor.id()).orElseThrow();
        PropertyListing listing = new PropertyListing();
        listing.setSellerId(seller.getId());
        listing.setPurpose(ListingPurpose.valueOf(draft.purpose()));
        listing.setType(PropertyType.valueOf(draft.type()));
        listing.setTitle(draft.title());
        listing.setState(draft.state());
        listing.setDistrict(draft.district());
        listing.setCity(draft.city());
        listing.setAddress(draft.address());
        listing.setAskingPrice(draft.askingPrice());
        listing.setMeasurements(draft.measurements());
        listing.setKhasraNumber(draft.khasraNumber());
        if (draft.ulpin() != null && !draft.ulpin().isBlank()) {
            listing.setUlpin(draft.ulpin().trim().toUpperCase(Locale.ROOT));
        }
        listing.setRegistryDetail(draft.registryDetail());
        listing.setHouseNumber(draft.houseNumber());
        listing.setFurnished(draft.furnished());
        listing.setFlatNumber(draft.flatNumber());
        listing.setFloor(draft.floor());
        listing.setBedrooms(draft.bedrooms());
        listing.setExtraNotes(draft.extraNotes());
        if (draft.latitude() != null && draft.longitude() != null) {
            listing.setLatitude(draft.latitude());
            listing.setLongitude(draft.longitude());
        }
        listing.setStatus(PropertyStatus.PENDING_AI);
        for (MultipartFile file : papers) {
            listing.getRegistryPapers().add(toStored(file));
        }
        if (photos != null) {
            for (MultipartFile photo : photos) {
                listing.getPropertyPhotos().add(toStored(photo));
            }
        }
        matchingService.run(listing, seller);
        ensureCoordinates(listing);
        listing.setUpdatedAt(Instant.now());
        store.saveProperty(listing);
        store.audit(seller.getId(), "PROPERTY_POSTED", listing.getId() + ":" + listing.getStatus());

        notifyService.notifyUser(seller, "Property submitted",
                "Property #" + listing.getId() + " status: " + listing.getStatus() + ". " + nullSafe(listing.getAiSummary()));
        if (listing.getStatus() == PropertyStatus.AI_VERIFIED_AWAITING_AUTHENTICATOR
                || listing.getStatus() == PropertyStatus.NEEDS_PHYSICAL_VERIFICATION
                || listing.getStatus() == PropertyStatus.PENDING_REGISTRY) {
            notifyService.notifyCityAuthenticators(
                    listing.getCity(),
                    "New case in your jurisdiction",
                    "Property #" + listing.getId() + " (" + listing.getTitle() + ") in " + listing.getCity()
                            + " needs attention. Queue: " + listing.getStatus()
            );
        }
        return toView(listing, true);
    }

    public List<PropertyView> mine(AuthUser actor) {
        return store.properties().stream()
                .filter(p -> actor.id().equals(p.getSellerId()) || actor.id().equals(p.getBuyerId()))
                .map(p -> toView(p, true))
                .toList();
    }

    public PropertyView officerView(AuthUser actor, Long id) {
        PropertyListing listing = requireInCity(actor, id);
        return toView(listing, true);
    }

    public PropertyView uploadVerificationReport(AuthUser actor, Long id, MultipartFile report) {
        if (actor.role() != Role.AUTHENTICATOR) {
            throw new ApiException(403, "Only an approved authenticator can upload a verification report");
        }
        PropertyListing listing = requireInCity(actor, id);
        if (report == null || report.isEmpty()) {
            throw new ApiException(400, "Verification report file is required");
        }
        String ct = report.getContentType() == null ? "" : report.getContentType().toLowerCase(Locale.ROOT);
        String name = report.getOriginalFilename() == null ? "" : report.getOriginalFilename().toLowerCase(Locale.ROOT);
        boolean ok = ct.contains("pdf") || ct.contains("image") || name.endsWith(".pdf")
                || name.endsWith(".png") || name.endsWith(".jpg") || name.endsWith(".jpeg") || name.endsWith(".webp");
        if (!ok) {
            throw new ApiException(400, "Verification report must be a PDF or image");
        }
        listing.setVerificationReport(toStored(report));
        listing.setUpdatedAt(Instant.now());
        store.saveProperty(listing);
        store.audit(actor.id(), "VERIFICATION_REPORT", String.valueOf(id));
        return toView(listing, true);
    }

    public PropertyView decide(AuthUser actor, Long id, boolean approve, String remarks) {
        if (actor.role() != Role.AUTHENTICATOR) {
            throw new ApiException(403, "Only an approved authenticator can decide");
        }
        PropertyListing listing = requireInCity(actor, id);
        if (listing.getStatus() != PropertyStatus.AI_VERIFIED_AWAITING_AUTHENTICATOR
                && listing.getStatus() != PropertyStatus.NEEDS_PHYSICAL_VERIFICATION
                && listing.getStatus() != PropertyStatus.PENDING_REGISTRY) {
            throw new ApiException(400, "This listing is not awaiting verification approval");
        }
        if (approve && listing.getStatus() == PropertyStatus.NEEDS_PHYSICAL_VERIFICATION
                && (listing.getVerificationReport() == null || listing.getVerificationReport().getBytes() == null)) {
            throw new ApiException(400, "Upload a physical verification report before approving this case");
        }
        listing.setOfficerRemarks(remarks);
        listing.setUpdatedAt(Instant.now());
        UserAccount seller = store.user(listing.getSellerId()).orElseThrow();
        if (approve) {
            ensureCoordinates(listing);
            listing.setVirtualJamabandi(virtualJamabandiService.generate(listing, seller));
            upsertGovernmentFromListing(listing, seller);
            listing.setStatus(PropertyStatus.LIVE);
            String location = listing.getAddress() + ", " + listing.getCity();
            notifyService.notifyUser(seller, "Your property is now live",
                    "Property #" + listing.getId() + " at " + location + " is approved and visible on search.");
        } else {
            listing.setStatus(PropertyStatus.REJECTED);
            notifyService.notifyUser(seller, "Property listing rejected",
                    "Property #" + listing.getId() + " was rejected. Remarks: " + nullSafe(remarks));
        }
        store.saveProperty(listing);
        store.audit(actor.id(), approve ? "APPROVED" : "REJECTED", String.valueOf(id));
        return toView(listing, true);
    }

    public StoredFile verificationReportBytes(AuthUser actor, Long id) {
        PropertyListing listing = requireInCity(actor, id);
        if (listing.getVerificationReport() == null) {
            throw new ApiException(404, "No verification report uploaded");
        }
        return listing.getVerificationReport();
    }

    public StoredFile virtualJamabandiBytes(AuthUser actor, Long id) {
        PropertyListing listing = store.property(id).orElseThrow(() -> new ApiException(404, "Property not found"));
        boolean allowed = actor.id().equals(listing.getSellerId())
                || actor.id().equals(listing.getBuyerId())
                || actor.role() == Role.ADMIN
                || (actor.role() == Role.AUTHENTICATOR
                && listing.getCity() != null
                && listing.getCity().equalsIgnoreCase(actor.city()));
        if (!allowed) {
            throw new ApiException(403, "You cannot download this jamabandi");
        }
        if (listing.getVirtualJamabandi() == null) {
            throw new ApiException(404, "Virtual jamabandi not generated yet");
        }
        return listing.getVirtualJamabandi();
    }

    public PropertyView requestPurchase(AuthUser actor, Long id) {
        if (actor.role() != Role.USER) {
            throw new ApiException(403, "Only signed-in users can request a purchase");
        }
        PropertyListing listing = store.property(id).orElseThrow(() -> new ApiException(404, "Property not found"));
        if (listing.getStatus() != PropertyStatus.LIVE || listing.getPurpose() != ListingPurpose.SALE) {
            throw new ApiException(400, "Only live sale listings can be purchased");
        }
        if (actor.id().equals(listing.getSellerId())) {
            throw new ApiException(400, "You cannot buy your own listing");
        }
        listing.setBuyerId(actor.id());
        listing.setStatus(PropertyStatus.PURCHASE_REQUESTED);
        listing.setPurchaseRequestedAt(Instant.now());
        listing.setUpdatedAt(Instant.now());
        store.saveProperty(listing);
        store.audit(actor.id(), "PURCHASE_REQUESTED", String.valueOf(id));

        UserAccount seller = store.user(listing.getSellerId()).orElseThrow();
        UserAccount buyer = store.user(actor.id()).orElseThrow();
        notifyService.notifyUser(seller, "Purchase request received",
                buyer.getFullName() + " requested to buy property #" + id + " (" + listing.getTitle() + "). Confirm from Track.");
        notifyService.notifyUser(buyer, "Purchase request sent",
                "Your purchase request for property #" + id + " was sent to the seller.");
        return toView(listing, true);
    }

    public PropertyView confirmSale(AuthUser actor, Long id) {
        if (actor.role() != Role.USER) {
            throw new ApiException(403, "Only the listing owner can confirm the sale");
        }
        PropertyListing listing = store.property(id).orElseThrow(() -> new ApiException(404, "Property not found"));
        if (!actor.id().equals(listing.getSellerId())) {
            throw new ApiException(403, "Not your listing");
        }
        if (listing.getStatus() != PropertyStatus.PURCHASE_REQUESTED || listing.getBuyerId() == null) {
            throw new ApiException(400, "No pending purchase request to confirm");
        }
        listing.setStatus(PropertyStatus.PENDING_TRANSFER);
        listing.setSaleConfirmedAt(Instant.now());
        listing.setUpdatedAt(Instant.now());
        store.saveProperty(listing);
        store.audit(actor.id(), "SALE_CONFIRMED", String.valueOf(id));

        UserAccount buyer = store.user(listing.getBuyerId()).orElseThrow();
        notifyService.notifyUser(buyer, "Seller confirmed the sale",
                "Property #" + id + " is awaiting city verifier finalization of ownership transfer.");
        notifyService.notifyCityAuthenticators(
                listing.getCity(),
                "Ownership transfer pending",
                "Property #" + id + " in " + listing.getCity() + " needs transfer finalization after seller confirmation."
        );
        return toView(listing, true);
    }

    public PropertyView finalizeTransfer(AuthUser actor, Long id) {
        if (actor.role() != Role.AUTHENTICATOR) {
            throw new ApiException(403, "Only an approved authenticator can finalize transfer");
        }
        PropertyListing listing = requireInCity(actor, id);
        if (listing.getStatus() != PropertyStatus.PENDING_TRANSFER || listing.getBuyerId() == null) {
            throw new ApiException(400, "Listing is not pending ownership transfer");
        }
        UserAccount buyer = store.user(listing.getBuyerId()).orElseThrow();
        UserAccount seller = store.user(listing.getSellerId()).orElseThrow();
        UserAccount officer = store.user(actor.id()).orElseThrow();

        String oldOwner = store.government(listing.getKhasraNumber())
                .map(GovernmentRecord::getOwnerName)
                .orElse(seller.getFullName());
        String village = store.government(listing.getKhasraNumber())
                .map(GovernmentRecord::getVillage)
                .orElse(listing.getCity());

        if (listing.getKhasraNumber() != null && !listing.getKhasraNumber().isBlank()) {
            store.government(listing.getKhasraNumber()).ifPresentOrElse(record -> {
                record.setOwnerName(buyer.getFullName());
                record.setOwnerPhone(buyer.getPhone());
                store.putGovernment(record);
            }, () -> {
                GovernmentRecord record = new GovernmentRecord(
                        listing.getKhasraNumber(),
                        village,
                        listing.getCity(),
                        listing.getDistrict(),
                        buyer.getFullName(),
                        listing.getMeasurements()
                );
                record.setOwnerPhone(buyer.getPhone());
                store.putGovernment(record);
            });
        }

        TransferCertificate certificate = new TransferCertificate();
        certificate.setPropertyId(listing.getId());
        certificate.setCertificateNumber("HR-FBD-TOC-" + listing.getId() + "-" + Instant.now().getEpochSecond());
        certificate.setKhasraNumber(listing.getKhasraNumber());
        certificate.setOldOwnerName(oldOwner);
        certificate.setNewOwnerName(buyer.getFullName());
        certificate.setVillage(village);
        certificate.setCity(listing.getCity());
        certificate.setDistrict(listing.getDistrict());
        certificate.setState(listing.getState());
        certificate.setMeasurements(listing.getMeasurements());
        certificate.setOfficerId(officer.getId());
        certificate.setOfficerName(officer.getFullName());
        certificate.setPdfBytes(certificateService.render(certificate));
        store.saveCertificate(certificate);

        listing.setCertificateId(certificate.getId());
        listing.setStatus(PropertyStatus.SOLD);
        listing.setTransferredAt(Instant.now());
        listing.setUpdatedAt(Instant.now());
        listing.setOfficerRemarks("Ownership transfer finalized. Certificate " + certificate.getCertificateNumber());
        store.saveProperty(listing);
        store.audit(actor.id(), "TRANSFER_FINALIZED", listing.getId() + ":" + certificate.getId());

        String certMsg = "Ownership transferred. Certificate " + certificate.getCertificateNumber()
                + " is ready. Download from Track / Certificates.";
        notifyService.notifyUser(buyer, "Ownership transferred", certMsg);
        notifyService.notifyUser(seller, "Sale completed — listing removed",
                "Property #" + id + " is sold and removed from marketplace. " + certMsg);
        return toView(listing, true);
    }

    public TransferCertificate getCertificate(AuthUser actor, Long certificateId) {
        TransferCertificate certificate = store.certificate(certificateId)
                .orElseThrow(() -> new ApiException(404, "Certificate not found"));
        PropertyListing listing = store.property(certificate.getPropertyId())
                .orElseThrow(() -> new ApiException(404, "Property not found"));
        boolean allowed = actor.id().equals(listing.getSellerId())
                || actor.id().equals(listing.getBuyerId())
                || (actor.role() == Role.AUTHENTICATOR
                && listing.getCity() != null
                && listing.getCity().equalsIgnoreCase(actor.city()))
                || actor.role() == Role.ADMIN;
        if (!allowed) {
            throw new ApiException(403, "You cannot download this certificate");
        }
        return certificate;
    }

    public AuthenticatorQueues queues(AuthUser actor) {
        if (actor.role() != Role.AUTHENTICATOR) {
            throw new ApiException(403, "Authenticator login required");
        }
        String city = actor.city();
        List<PropertyView> inCity = store.properties().stream()
                .filter(p -> p.getCity() != null && p.getCity().equalsIgnoreCase(city))
                .map(p -> toView(p, true))
                .toList();
        return new AuthenticatorQueues(
                inCity.stream().filter(p -> p.status() == PropertyStatus.AI_VERIFIED_AWAITING_AUTHENTICATOR).toList(),
                inCity.stream().filter(p -> p.status() == PropertyStatus.NEEDS_PHYSICAL_VERIFICATION).toList(),
                inCity.stream().filter(p -> p.status() == PropertyStatus.PENDING_REGISTRY).toList(),
                inCity.stream().filter(p -> p.status() == PropertyStatus.PENDING_TRANSFER).toList()
        );
    }

    private PropertyListing requireInCity(AuthUser actor, Long id) {
        PropertyListing listing = store.property(id).orElseThrow(() -> new ApiException(404, "Property not found"));
        if (actor.role() == Role.AUTHENTICATOR
                && (listing.getCity() == null || !listing.getCity().equalsIgnoreCase(actor.city()))) {
            throw new ApiException(403, "This land is outside your working city");
        }
        return listing;
    }

    private boolean match(String filter, String value) {
        if (filter == null || filter.isBlank() || "ALL".equalsIgnoreCase(filter)) {
            return true;
        }
        return value != null && value.equalsIgnoreCase(filter);
    }

    private StoredFile toStored(MultipartFile file) {
        try {
            StoredFile stored = new StoredFile();
            stored.setId(UUID.randomUUID().toString());
            stored.setOriginalName(file.getOriginalFilename());
            stored.setContentType(file.getContentType());
            stored.setBytes(file.getBytes());
            return stored;
        } catch (Exception ex) {
            throw new ApiException(400, "Could not read uploaded paper");
        }
    }

    private String nullSafe(String value) {
        return value == null ? "" : value;
    }

    private void ensureCoordinates(PropertyListing listing) {
        if (listing.getLatitude() != null && listing.getLongitude() != null) {
            return;
        }
        if (listing.getUlpin() != null && !listing.getUlpin().isBlank()) {
            double[] decoded = UlpinCodec.decode(listing.getUlpin());
            if (decoded != null) {
                listing.setLatitude(decoded[0]);
                listing.setLongitude(decoded[1]);
                return;
            }
        }
        double[] city = GeoCentroids.forCity(listing.getCity());
        if (city != null) {
            listing.setLatitude(city[0]);
            listing.setLongitude(city[1]);
        }
    }

    private void upsertGovernmentFromListing(PropertyListing listing, UserAccount seller) {
        String khasra = listing.getKhasraNumber();
        if (khasra == null || khasra.isBlank()) {
            khasra = listing.getSurveyNumber();
        }
        if (khasra == null || khasra.isBlank()) {
            return;
        }
        final String key = khasra;
        store.government(key).ifPresentOrElse(record -> {
            if (listing.getUlpin() != null && !listing.getUlpin().isBlank()) {
                record.setUlpin(listing.getUlpin());
            }
            store.putGovernment(record);
        }, () -> {
            GovernmentRecord record = new GovernmentRecord(
                    key,
                    listing.getCity(),
                    listing.getCity(),
                    listing.getDistrict(),
                    seller.getFullName(),
                    listing.getMeasurements()
            );
            record.setUlpin(listing.getUlpin());
            record.setSurveyNumber(listing.getSurveyNumber());
            record.setKhataNumber(listing.getKhataNumber());
            record.setKhewatNumber(listing.getKhewatNumber());
            record.setKhatauniNumber(listing.getKhatauniNumber());
            record.setOwnerPhone(seller.getPhone());
            store.putGovernment(record);
        });
    }

    public StoredFile photoBytes(Long propertyId, int index) {
        PropertyListing listing = store.property(propertyId).orElseThrow(() -> new ApiException(404, "Property not found"));
        if (listing.getPropertyPhotos() == null || index < 0 || index >= listing.getPropertyPhotos().size()) {
            throw new ApiException(404, "Photo not found");
        }
        return listing.getPropertyPhotos().get(index);
    }

    PropertyView toView(PropertyListing p, boolean includeSensitive) {
        Long sellerId = p.getSellerId();
        String sellerName = store.user(sellerId).map(UserAccount::getFullName).orElse("Seller");
        String buyerName = p.getBuyerId() == null
                ? null
                : store.user(p.getBuyerId()).map(UserAccount::getFullName).orElse(null);
        List<String> paperNames = includeSensitive
                ? p.getRegistryPapers().stream().map(StoredFile::getOriginalName).toList()
                : List.of();
        int photoCount = p.getPropertyPhotos() == null ? 0 : p.getPropertyPhotos().size();
        String coverPhotoUrl = photoCount > 0 ? "/api/public/properties/" + p.getId() + "/photos/0" : null;
        String locateUrl = null;
        if (p.getLatitude() != null && p.getLongitude() != null) {
            locateUrl = UlpinCodec.locateUrl(p.getLatitude(), p.getLongitude());
        }
        boolean hasReport = p.getVerificationReport() != null && p.getVerificationReport().getBytes() != null;
        boolean hasJamabandi = p.getVirtualJamabandi() != null && p.getVirtualJamabandi().getBytes() != null;
        return new PropertyView(
                p.getId(),
                sellerId,
                sellerName,
                p.getBuyerId(),
                buyerName,
                p.getPurpose(),
                p.getType(),
                p.getStatus(),
                p.getTitle(),
                p.getState(),
                p.getDistrict(),
                p.getCity(),
                p.getAddress(),
                p.getAskingPrice(),
                p.getMeasurements(),
                includeSensitive ? p.getKhasraNumber() : null,
                includeSensitive ? p.getUlpin() : p.getUlpin(),
                includeSensitive ? p.getSurveyNumber() : null,
                includeSensitive ? p.getKhataNumber() : null,
                includeSensitive ? p.getKhewatNumber() : null,
                includeSensitive ? p.getKhatauniNumber() : null,
                includeSensitive ? p.getRegistryDetail() : null,
                p.getHouseNumber(),
                p.getFurnished(),
                p.getFlatNumber(),
                p.getFloor(),
                p.getBedrooms(),
                includeSensitive ? p.getExtraNotes() : null,
                includeSensitive ? p.getAiSummary() : null,
                includeSensitive ? p.getOfficerRemarks() : null,
                paperNames,
                coverPhotoUrl,
                photoCount,
                p.getCertificateId(),
                p.getCreatedAt(),
                p.getLatitude(),
                p.getLongitude(),
                locateUrl,
                includeSensitive && hasReport,
                includeSensitive && hasReport ? p.getVerificationReport().getOriginalName() : null,
                includeSensitive && hasJamabandi
        );
    }

    public record PropertyDraft(
            String purpose,
            String type,
            String title,
            String state,
            String district,
            String city,
            String address,
            Double askingPrice,
            String measurements,
            String khasraNumber,
            String ulpin,
            String registryDetail,
            String houseNumber,
            Boolean furnished,
            String flatNumber,
            Integer floor,
            Integer bedrooms,
            String extraNotes,
            Double latitude,
            Double longitude
    ) {}

    public record PropertyView(
            Long id,
            Long sellerId,
            String sellerName,
            Long buyerId,
            String buyerName,
            ListingPurpose purpose,
            PropertyType type,
            PropertyStatus status,
            String title,
            String state,
            String district,
            String city,
            String address,
            Double askingPrice,
            String measurements,
            String khasraNumber,
            String ulpin,
            String surveyNumber,
            String khataNumber,
            String khewatNumber,
            String khatauniNumber,
            String registryDetail,
            String houseNumber,
            Boolean furnished,
            String flatNumber,
            Integer floor,
            Integer bedrooms,
            String extraNotes,
            String aiSummary,
            String officerRemarks,
            List<String> registryPaperNames,
            String coverPhotoUrl,
            int photoCount,
            Long certificateId,
            Instant createdAt,
            Double latitude,
            Double longitude,
            String locateUrl,
            boolean hasVerificationReport,
            String verificationReportName,
            boolean hasVirtualJamabandi
    ) {}

    public record AuthenticatorQueues(
            List<PropertyView> aiVerified,
            List<PropertyView> physicalVerification,
            List<PropertyView> registry,
            List<PropertyView> pendingTransfer
    ) {}
}
