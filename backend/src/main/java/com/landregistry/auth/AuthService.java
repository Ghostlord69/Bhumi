package com.landregistry.auth;

import com.landregistry.common.ApiException;
import com.landregistry.domain.AuthenticatorApplication;
import com.landregistry.domain.UserAccount;
import com.landregistry.security.AuthUser;
import com.landregistry.security.JwtService;
import com.landregistry.security.Role;
import com.landregistry.store.AppStore;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {
    private final AppStore store;
    private final PasswordEncoder encoder;
    private final JwtService jwtService;

    public AuthService(AppStore store, PasswordEncoder encoder, JwtService jwtService) {
        this.store = store;
        this.encoder = encoder;
        this.jwtService = jwtService;
    }

    public TokenResponse register(RegisterRequest request) {
        if (store.userByEmail(request.email()).isPresent()) {
            throw new ApiException(409, "An account already exists for this email");
        }
        Role role = Role.USER;
        if (request.role() != null && !request.role().isBlank()) {
            Role requested = Role.valueOf(request.role());
            if (requested == Role.ADMIN) {
                throw new ApiException(403, "Admin accounts cannot be created by signup. Admins log in with issued credentials only.");
            }
            if (requested == Role.AUTHENTICATOR) {
                throw new ApiException(400, "Authenticators must apply; use the authenticator application form");
            }
            role = Role.USER;
        }
        UserAccount user = new UserAccount();
        user.setEmail(request.email().trim());
        user.setPhone(request.phone());
        user.setPasswordHash(encoder.encode(request.password()));
        user.setFullName(request.fullName());
        user.setRole(role);
        store.saveUser(user);
        return token(user);
    }

    public TokenResponse applyAuthenticator(AuthenticatorApplyRequest request) {
        UserAccount pending = store.userByEmail(request.personalEmail()).orElseGet(() -> {
            UserAccount user = new UserAccount();
            user.setEmail(request.personalEmail().trim());
            user.setPhone(request.phone());
            user.setPasswordHash(encoder.encode(request.password()));
            user.setFullName(request.fullName());
            user.setRole(Role.AUTHENTICATOR);
            user.setActive(false);
            user.setState(request.state());
            user.setDistrict(request.district());
            user.setCity(request.city());
            return store.saveUser(user);
        });
        pending.setRole(Role.AUTHENTICATOR);
        pending.setActive(false);
        pending.setCity(request.city());
        pending.setDistrict(request.district());
        pending.setState(request.state());
        store.saveUser(pending);

        AuthenticatorApplication application = new AuthenticatorApplication();
        application.setApplicantUserId(pending.getId());
        application.setFullName(request.fullName());
        application.setPersonalEmail(request.personalEmail());
        application.setPhone(request.phone());
        application.setOfficialIdNumber(request.officialIdNumber());
        application.setState(request.state());
        application.setDistrict(request.district());
        application.setCity(request.city());
        application.setStatus("PENDING");
        store.saveApplication(application);
        store.audit(pending.getId(), "AUTHENTICATOR_APPLY", request.city());
        return new TokenResponse(null, pending.getId(), Role.AUTHENTICATOR, pending.getFullName(), false,
                "Application submitted. A state admin must approve you before you can sign in.",
                pending.getCity(), pending.getDistrict(), pending.getState());
    }

    public TokenResponse login(LoginRequest request) {
        UserAccount user = store.userByEmail(request.email())
                .orElseThrow(() -> new ApiException(401, "Invalid email or password"));
        if (!encoder.matches(request.password(), user.getPasswordHash())) {
            throw new ApiException(401, "Invalid email or password");
        }
        if (!user.isActive()) {
            throw new ApiException(403, "This account is waiting for ministry approval");
        }
        return token(user);
    }

    public TokenResponse me(AuthUser principal) {
        UserAccount user = store.user(principal.id()).orElseThrow(() -> new ApiException(401, "Unknown user"));
        return token(user);
    }

    private TokenResponse token(UserAccount user) {
        AuthUser principal = new AuthUser(
                user.getId(), user.getRole(), user.getEmail(), user.getCity(), user.getDistrict(), user.getState());
        return new TokenResponse(
                jwtService.issue(principal),
                user.getId(),
                user.getRole(),
                user.getFullName(),
                user.isActive(),
                null,
                user.getCity(),
                user.getDistrict(),
                user.getState()
        );
    }

    public record RegisterRequest(String email, String password, String fullName, String phone, String role) {}

    public record LoginRequest(String email, String password) {}

    public record AuthenticatorApplyRequest(
            String fullName,
            String personalEmail,
            String phone,
            String password,
            String officialIdNumber,
            String state,
            String district,
            String city
    ) {}

    public record TokenResponse(
            String token,
            Long userId,
            Role role,
            String fullName,
            boolean active,
            String message,
            String city,
            String district,
            String state
    ) {}
}
