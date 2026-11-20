package com.landregistry.domain;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

public class PropertyListing {
    private Long id;
    private Long sellerId;
    private ListingPurpose purpose;
    private PropertyType type;
    private PropertyStatus status;
    private String title;
    private String state;
    private String district;
    private String city;
    private String address;
    private Double askingPrice;
    private String measurements;
    private String khasraNumber;
    private String ulpin;
    private String surveyNumber;
    private String khataNumber;
    private String khewatNumber;
    private String khatauniNumber;
    private String registryDetail;
    private String houseNumber;
    private Boolean furnished;
    private String flatNumber;
    private Integer floor;
    private Integer bedrooms;
    private String extraNotes;
    private List<StoredFile> registryPapers = new ArrayList<>();
    private List<StoredFile> propertyPhotos = new ArrayList<>();
    private Double latitude;
    private Double longitude;
    private StoredFile verificationReport;
    private StoredFile virtualJamabandi;
    private String aiSummary;
    private String officerRemarks;
    private Long buyerId;
    private Long certificateId;
    private Instant purchaseRequestedAt;
    private Instant saleConfirmedAt;
    private Instant transferredAt;
    private Instant createdAt = Instant.now();
    private Instant updatedAt = Instant.now();

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getSellerId() { return sellerId; }
    public void setSellerId(Long sellerId) { this.sellerId = sellerId; }
    public ListingPurpose getPurpose() { return purpose; }
    public void setPurpose(ListingPurpose purpose) { this.purpose = purpose; }
    public PropertyType getType() { return type; }
    public void setType(PropertyType type) { this.type = type; }
    public PropertyStatus getStatus() { return status; }
    public void setStatus(PropertyStatus status) { this.status = status; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getState() { return state; }
    public void setState(String state) { this.state = state; }
    public String getDistrict() { return district; }
    public void setDistrict(String district) { this.district = district; }
    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }
    public String getAddress() { return address; }
    public void setAddress(String address) { this.address = address; }
    public Double getAskingPrice() { return askingPrice; }
    public void setAskingPrice(Double askingPrice) { this.askingPrice = askingPrice; }
    public String getMeasurements() { return measurements; }
    public void setMeasurements(String measurements) { this.measurements = measurements; }
    public String getKhasraNumber() { return khasraNumber; }
    public void setKhasraNumber(String khasraNumber) { this.khasraNumber = khasraNumber; }
    public String getUlpin() { return ulpin; }
    public void setUlpin(String ulpin) { this.ulpin = ulpin; }
    public String getSurveyNumber() { return surveyNumber; }
    public void setSurveyNumber(String surveyNumber) { this.surveyNumber = surveyNumber; }
    public String getKhataNumber() { return khataNumber; }
    public void setKhataNumber(String khataNumber) { this.khataNumber = khataNumber; }
    public String getKhewatNumber() { return khewatNumber; }
    public void setKhewatNumber(String khewatNumber) { this.khewatNumber = khewatNumber; }
    public String getKhatauniNumber() { return khatauniNumber; }
    public void setKhatauniNumber(String khatauniNumber) { this.khatauniNumber = khatauniNumber; }
    public String getRegistryDetail() { return registryDetail; }
    public void setRegistryDetail(String registryDetail) { this.registryDetail = registryDetail; }
    public String getHouseNumber() { return houseNumber; }
    public void setHouseNumber(String houseNumber) { this.houseNumber = houseNumber; }
    public Boolean getFurnished() { return furnished; }
    public void setFurnished(Boolean furnished) { this.furnished = furnished; }
    public String getFlatNumber() { return flatNumber; }
    public void setFlatNumber(String flatNumber) { this.flatNumber = flatNumber; }
    public Integer getFloor() { return floor; }
    public void setFloor(Integer floor) { this.floor = floor; }
    public Integer getBedrooms() { return bedrooms; }
    public void setBedrooms(Integer bedrooms) { this.bedrooms = bedrooms; }
    public String getExtraNotes() { return extraNotes; }
    public void setExtraNotes(String extraNotes) { this.extraNotes = extraNotes; }
    public List<StoredFile> getRegistryPapers() { return registryPapers; }
    public void setRegistryPapers(List<StoredFile> registryPapers) { this.registryPapers = registryPapers; }
    public List<StoredFile> getPropertyPhotos() { return propertyPhotos; }
    public void setPropertyPhotos(List<StoredFile> propertyPhotos) { this.propertyPhotos = propertyPhotos; }
    public Double getLatitude() { return latitude; }
    public void setLatitude(Double latitude) { this.latitude = latitude; }
    public Double getLongitude() { return longitude; }
    public void setLongitude(Double longitude) { this.longitude = longitude; }
    public StoredFile getVerificationReport() { return verificationReport; }
    public void setVerificationReport(StoredFile verificationReport) { this.verificationReport = verificationReport; }
    public StoredFile getVirtualJamabandi() { return virtualJamabandi; }
    public void setVirtualJamabandi(StoredFile virtualJamabandi) { this.virtualJamabandi = virtualJamabandi; }
    public String getAiSummary() { return aiSummary; }
    public void setAiSummary(String aiSummary) { this.aiSummary = aiSummary; }
    public String getOfficerRemarks() { return officerRemarks; }
    public void setOfficerRemarks(String officerRemarks) { this.officerRemarks = officerRemarks; }
    public Long getBuyerId() { return buyerId; }
    public void setBuyerId(Long buyerId) { this.buyerId = buyerId; }
    public Long getCertificateId() { return certificateId; }
    public void setCertificateId(Long certificateId) { this.certificateId = certificateId; }
    public Instant getPurchaseRequestedAt() { return purchaseRequestedAt; }
    public void setPurchaseRequestedAt(Instant purchaseRequestedAt) { this.purchaseRequestedAt = purchaseRequestedAt; }
    public Instant getSaleConfirmedAt() { return saleConfirmedAt; }
    public void setSaleConfirmedAt(Instant saleConfirmedAt) { this.saleConfirmedAt = saleConfirmedAt; }
    public Instant getTransferredAt() { return transferredAt; }
    public void setTransferredAt(Instant transferredAt) { this.transferredAt = transferredAt; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(Instant updatedAt) { this.updatedAt = updatedAt; }
}
