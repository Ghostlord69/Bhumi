package com.landregistry.security;

public record AuthUser(Long id, Role role, String email, String city, String district, String state) {}
