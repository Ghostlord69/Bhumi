package com.landregistry.domain;

import java.time.Instant;

public class StateAdmin {
    private Long adminId;
    private Long userId;
    private String stateUnionTerritory;
    private String email;
    private String phone;
    private String fullName;
    private boolean active = true;
    private Instant createdAt = Instant.now();

    public Long getAdminId() { return adminId; }
    public void setAdminId(Long adminId) { this.adminId = adminId; }
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    public String getStateUnionTerritory() { return stateUnionTerritory; }
    public void setStateUnionTerritory(String stateUnionTerritory) { this.stateUnionTerritory = stateUnionTerritory; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }
    public String getFullName() { return fullName; }
    public void setFullName(String fullName) { this.fullName = fullName; }
    public boolean isActive() { return active; }
    public void setActive(boolean active) { this.active = active; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
}
