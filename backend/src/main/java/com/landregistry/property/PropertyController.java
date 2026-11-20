package com.landregistry.property;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.landregistry.domain.TransferCertificate;
import com.landregistry.location.LocationCatalog;
import com.landregistry.security.AuthUser;
import com.landregistry.security.SecurityUtil;
import java.util.List;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
public class PropertyController {
    private final PropertyService propertyService;
    private final LocationCatalog locations;
    private final ObjectMapper mapper;

    public PropertyController(PropertyService propertyService, LocationCatalog locations, ObjectMapper mapper) {
        this.propertyService = propertyService;
        this.locations = locations;
        this.mapper = mapper;
    }

    @GetMapping("/api/public/locations/states")
    public List<String> states() {
        return locations.states();
    }

    @GetMapping("/api/public/locations/districts")
    public List<String> districts(@RequestParam String state) {
        return locations.districts(state);
    }

    @GetMapping("/api/public/locations/cities")
    public List<String> cities(@RequestParam String state, @RequestParam String district) {
        return locations.cities(state, district);
    }

    @GetMapping("/api/public/properties")
    public List<PropertyService.PropertyView> search(
            @RequestParam(required = false) String type,
            @RequestParam(required = false) String state,
            @RequestParam(required = false) String district,
            @RequestParam(required = false) String city,
            @RequestParam(required = false) Double minPrice,
            @RequestParam(required = false) Double maxPrice
    ) {
        return propertyService.search(type, state, district, city, minPrice, maxPrice);
    }

    @GetMapping("/api/public/properties/recommended")
    public List<PropertyService.PropertyView> recommended(
            @RequestParam(required = false) String state,
            @RequestParam(required = false) String district,
            @RequestParam(required = false) String city
    ) {
        return propertyService.recommended(state, district, city);
    }

    @GetMapping("/api/public/properties/{id}")
    public PropertyService.PropertyView detail(@PathVariable Long id) {
        return propertyService.publicDetail(id);
    }

    @GetMapping("/api/properties/mine")
    public List<PropertyService.PropertyView> mine() {
        return propertyService.mine(SecurityUtil.current());
    }

    @PostMapping(value = "/api/properties", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public PropertyService.PropertyView create(
            @RequestPart("payload") String payload,
            @RequestPart("papers") List<MultipartFile> papers,
            @RequestPart(value = "photos", required = false) List<MultipartFile> photos
    ) throws Exception {
        AuthUser actor = SecurityUtil.current();
        PropertyService.PropertyDraft draft = mapper.readValue(payload, PropertyService.PropertyDraft.class);
        return propertyService.create(actor, draft, papers, photos);
    }

    @GetMapping("/api/public/properties/{id}/photos/{index}")
    public ResponseEntity<byte[]> publicPhoto(@PathVariable Long id, @PathVariable int index) {
        var photo = propertyService.photoBytes(id, index);
        MediaType type = MediaType.IMAGE_JPEG;
        if (photo.getContentType() != null && photo.getContentType().contains("png")) {
            type = MediaType.IMAGE_PNG;
        } else if (photo.getContentType() != null && photo.getContentType().contains("webp")) {
            type = MediaType.parseMediaType("image/webp");
        }
        return ResponseEntity.ok().contentType(type).body(photo.getBytes());
    }

    @PostMapping("/api/properties/{id}/purchase-request")
    public PropertyService.PropertyView purchaseRequest(@PathVariable Long id) {
        return propertyService.requestPurchase(SecurityUtil.current(), id);
    }

    @PostMapping("/api/properties/{id}/confirm-sale")
    public PropertyService.PropertyView confirmSale(@PathVariable Long id) {
        return propertyService.confirmSale(SecurityUtil.current(), id);
    }

    @GetMapping("/api/authenticator/queues")
    public PropertyService.AuthenticatorQueues queues() {
        return propertyService.queues(SecurityUtil.current());
    }

    @GetMapping("/api/authenticator/properties/{id}")
    public PropertyService.PropertyView officerDetail(@PathVariable Long id) {
        return propertyService.officerView(SecurityUtil.current(), id);
    }

    @PostMapping(value = "/api/authenticator/properties/{id}/verification-report", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public PropertyService.PropertyView uploadReport(
            @PathVariable Long id,
            @RequestPart("report") MultipartFile report
    ) {
        return propertyService.uploadVerificationReport(SecurityUtil.current(), id, report);
    }

    @GetMapping("/api/authenticator/properties/{id}/verification-report")
    public ResponseEntity<byte[]> downloadReport(@PathVariable Long id) {
        var report = propertyService.verificationReportBytes(SecurityUtil.current(), id);
        MediaType type = MediaType.APPLICATION_OCTET_STREAM;
        if (report.getContentType() != null) {
            type = MediaType.parseMediaType(report.getContentType());
        }
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        "attachment; filename=\"" + (report.getOriginalName() == null ? "report" : report.getOriginalName()) + "\"")
                .contentType(type)
                .body(report.getBytes());
    }

    @PostMapping("/api/authenticator/properties/{id}/decision")
    public PropertyService.PropertyView decide(
            @PathVariable Long id,
            @RequestParam boolean approve,
            @RequestParam(required = false, defaultValue = "") String remarks
    ) {
        return propertyService.decide(SecurityUtil.current(), id, approve, remarks);
    }

    @PostMapping("/api/authenticator/properties/{id}/finalize-transfer")
    public PropertyService.PropertyView finalizeTransfer(@PathVariable Long id) {
        return propertyService.finalizeTransfer(SecurityUtil.current(), id);
    }

    @GetMapping("/api/properties/{id}/virtual-jamabandi")
    public ResponseEntity<byte[]> virtualJamabandi(@PathVariable Long id) {
        var file = propertyService.virtualJamabandiBytes(SecurityUtil.current(), id);
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        "attachment; filename=\"" + (file.getOriginalName() == null ? "jamabandi.png" : file.getOriginalName()) + "\"")
                .contentType(MediaType.IMAGE_PNG)
                .body(file.getBytes());
    }

    @GetMapping("/api/certificates/{id}")
    public ResponseEntity<byte[]> certificate(@PathVariable Long id) {
        TransferCertificate certificate = propertyService.getCertificate(SecurityUtil.current(), id);
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        "attachment; filename=\"" + certificate.getCertificateNumber() + ".pdf\"")
                .contentType(MediaType.APPLICATION_PDF)
                .body(certificate.getPdfBytes());
    }
}
