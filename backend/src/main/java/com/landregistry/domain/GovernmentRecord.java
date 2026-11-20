package com.landregistry.domain;

import java.time.Instant;

public class GovernmentRecord {
    private String khasraNumber;
    private String ulpin;
    private String surveyNumber;
    private String khataNumber;
    private String khewatNumber;
    private String khatauniNumber;
    private String village;
    private String city;
    private String district;
    private String ownerName;
    private String measurements;
    private String ownerPhone;
    private Instant updatedAt = Instant.now();

    public GovernmentRecord() {}

    public GovernmentRecord(String khasraNumber, String village, String city, String district, String ownerName, String measurements) {
        this.khasraNumber = khasraNumber;
        this.village = village;
        this.city = city;
        this.district = district;
        this.ownerName = ownerName;
        this.measurements = measurements;
        this.updatedAt = Instant.now();
    }

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
    public String getVillage() { return village; }
    public void setVillage(String village) { this.village = village; }
    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }
    public String getDistrict() { return district; }
    public void setDistrict(String district) { this.district = district; }
    public String getOwnerName() { return ownerName; }
    public void setOwnerName(String ownerName) {
        this.ownerName = ownerName;
        this.updatedAt = Instant.now();
    }
    public String getMeasurements() { return measurements; }
    public void setMeasurements(String measurements) { this.measurements = measurements; }
    public String getOwnerPhone() { return ownerPhone; }
    public void setOwnerPhone(String ownerPhone) { this.ownerPhone = ownerPhone; }
    public Instant getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(Instant updatedAt) { this.updatedAt = updatedAt; }
}
