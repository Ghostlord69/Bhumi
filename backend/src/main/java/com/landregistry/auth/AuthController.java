package com.landregistry.auth;

import com.landregistry.security.SecurityUtil;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/register")
    public AuthService.TokenResponse register(@RequestBody @Valid AuthService.RegisterRequest request) {
        return authService.register(request);
    }

    @PostMapping("/login")
    public AuthService.TokenResponse login(@RequestBody AuthService.LoginRequest request) {
        return authService.login(request);
    }

    @PostMapping("/authenticator-apply")
    public AuthService.TokenResponse apply(@RequestBody AuthService.AuthenticatorApplyRequest request) {
        return authService.applyAuthenticator(request);
    }

    @GetMapping("/me")
    public AuthService.TokenResponse me() {
        return authService.me(SecurityUtil.current());
    }
}
