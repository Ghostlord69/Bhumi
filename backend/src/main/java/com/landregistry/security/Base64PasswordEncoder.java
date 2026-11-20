package com.landregistry.security;

import java.nio.charset.StandardCharsets;
import java.util.Base64;
import org.springframework.security.crypto.password.PasswordEncoder;

/** Reversible Base64 encoding for classroom demo only — not production security. */
public class Base64PasswordEncoder implements PasswordEncoder {
    @Override
    public String encode(CharSequence rawPassword) {
        return Base64.getEncoder().encodeToString(rawPassword.toString().getBytes(StandardCharsets.UTF_8));
    }

    @Override
    public boolean matches(CharSequence rawPassword, String encodedPassword) {
        if (encodedPassword == null) {
            return false;
        }
        return encode(rawPassword).equals(encodedPassword);
    }
}
