package com.landregistry.domain;

import java.time.Instant;

public class TransferCertificate {
    private Long id;
    private Long propertyId;
    private String certificateNumber;
    private String khasraNumber;
    private String oldOwnerName;
    private String newOwnerName;
    private String village;
    private String city;
    private String district;
    private String state;
    private String measurements;
    private Long officerId;
    private String officerName;
    private Instant issuedAt = Instant.now();
    private byte[] pdfBytes;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getPropertyId() { return propertyId; }
    public void setPropertyId(Long propertyId) { this.propertyId = propertyId; }
    public String getCertificateNumber() { return certificateNumber; }
    public void setCertificateNumber(String certificateNumber) { this.certificateNumber = certificateNumber; }
    public String getKhasraNumber() { return khasraNumber; }
    public void setKhasraNumber(String khasraNumber) { this.khasraNumber = khasraNumber; }
    public String getOldOwnerName() { return oldOwnerName; }
    public void setOldOwnerName(String oldOwnerName) { this.oldOwnerName = oldOwnerName; }
    public String getNewOwnerName() { return newOwnerName; }
    public void setNewOwnerName(String newOwnerName) { this.newOwnerName = newOwnerName; }
    public String getVillage() { return village; }
    public void setVillage(String village) { this.village = village; }
    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }
    public String getDistrict() { return district; }
    public void setDistrict(String district) { this.district = district; }
    public String getState() { return state; }
    public void setState(String state) { this.state = state; }
    public String getMeasurements() { return measurements; }
    public void setMeasurements(String measurements) { this.measurements = measurements; }
    public Long getOfficerId() { return officerId; }
    public void setOfficerId(Long officerId) { this.officerId = officerId; }
    public String getOfficerName() { return officerName; }
    public void setOfficerName(String officerName) { this.officerName = officerName; }
    public Instant getIssuedAt() { return issuedAt; }
    public void setIssuedAt(Instant issuedAt) { this.issuedAt = issuedAt; }
    public byte[] getPdfBytes() { return pdfBytes; }
    public void setPdfBytes(byte[] pdfBytes) { this.pdfBytes = pdfBytes; }
}
