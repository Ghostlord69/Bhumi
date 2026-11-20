package com.landregistry.admin;

import com.landregistry.common.ApiException;
import com.landregistry.domain.AuthenticatorApplication;
import com.landregistry.domain.StateAdmin;
import com.landregistry.domain.UserAccount;
import com.landregistry.notify.NotifyService;
import com.landregistry.security.AuthUser;
import com.landregistry.security.Role;
import com.landregistry.store.AppStore;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AdminService {
    private final AppStore store;
    private final PasswordEncoder encoder;
    private final NotifyService notifyService;

    public AdminService(AppStore store, PasswordEncoder encoder, NotifyService notifyService) {
        this.store = store;
        this.encoder = encoder;
        this.notifyService = notifyService;
    }

    public Dashboard dashboard(AuthUser actor) {
        StateAdmin admin = requireStateAdmin(actor);
        String state = admin.getStateUnionTerritory();
        List<AuthenticatorApplication> pending = store.applications().stream()
                .filter(a -> "PENDING".equals(a.getStatus()))
                .filter(a -> stateEquals(state, a.getState()))
                .toList();
        List<UserAccount> active = store.authenticators().stream()
                .filter(UserAccount::isActive)
                .filter(a -> stateEquals(state, a.getState()))
                .toList();
        List<AuthenticatorApplication> rejected = store.applications().stream()
                .filter(a -> "REJECTED".equals(a.getStatus()))
                .filter(a -> stateEquals(state, a.getState()))
                .toList();
        return new Dashboard(
                admin.getAdminId(),
                admin.getFullName(),
                state,
                admin.getEmail(),
                admin.getPhone(),
                active.stream().map(this::toOfficer).toList(),
                pending.stream().map(this::toApp).toList(),
                rejected.stream().map(this::toApp).toList()
        );
    }

    public OfficerView approve(AuthUser actor, Long applicationId) {
        StateAdmin admin = requireStateAdmin(actor);
        AuthenticatorApplication application = requireApplicationInState(admin, applicationId);
        if (!"PENDING".equals(application.getStatus())) {
            throw new ApiException(400, "Only pending applications can be approved");
        }
        UserAccount officer = store.user(application.getApplicantUserId()).orElseThrow();
        String login = officialLogin(application);
        String password = "Auth@" + UUID.randomUUID().toString().substring(0, 8);
        officer.setActive(true);
        officer.setRole(Role.AUTHENTICATOR);
        officer.setOfficialLogin(login);
        officer.setEmail(login);
        officer.setPasswordHash(encoder.encode(password));
        officer.setCity(application.getCity());
        officer.setDistrict(application.getDistrict());
        officer.setState(application.getState());
        store.saveUser(officer);
        application.setStatus("APPROVED");
        store.saveApplication(application);
        notifyService.email(
                application.getPersonalEmail(),
                "Authenticator account approved",
                "Official login: " + login + " | Temporary password: " + password
                        + " | Working city: " + application.getCity()
                        + " | State: " + application.getState()
        );
        store.audit(actor.id(), "AUTHENTICATOR_APPROVED", login);
        return toOfficer(officer);
    }

    public ApplicationView reject(AuthUser actor, Long applicationId, String remarks) {
        StateAdmin admin = requireStateAdmin(actor);
        AuthenticatorApplication application = requireApplicationInState(admin, applicationId);
        if (!"PENDING".equals(application.getStatus())) {
            throw new ApiException(400, "Only pending applications can be rejected");
        }
        application.setStatus("REJECTED");
        store.saveApplication(application);
        UserAccount applicant = store.user(application.getApplicantUserId()).orElse(null);
        if (applicant != null) {
            applicant.setActive(false);
            store.saveUser(applicant);
            notifyService.notifyUser(
                    applicant,
                    "Authenticator application rejected",
                    "Your application for " + application.getCity() + ", " + application.getState()
                            + " was rejected by the state admin."
                            + (remarks == null || remarks.isBlank() ? "" : " Remarks: " + remarks)
            );
        }
        store.audit(actor.id(), "AUTHENTICATOR_REJECTED", String.valueOf(applicationId));
        return toApp(application);
    }

    private AuthenticatorApplication requireApplicationInState(StateAdmin admin, Long applicationId) {
        AuthenticatorApplication application = store.application(applicationId)
                .orElseThrow(() -> new ApiException(404, "Application not found"));
        if (!stateEquals(admin.getStateUnionTerritory(), application.getState())) {
            throw new ApiException(403, "This applicant is outside your state / union territory");
        }
        return application;
    }

    private StateAdmin requireStateAdmin(AuthUser actor) {
        if (actor.role() != Role.ADMIN) {
            throw new ApiException(403, "State admin only");
        }
        return store.stateAdminByUserId(actor.id())
                .filter(StateAdmin::isActive)
                .orElseThrow(() -> new ApiException(403, "No state admin profile linked to this account"));
    }

    private boolean stateEquals(String left, String right) {
        return left != null && right != null && left.trim().equalsIgnoreCase(right.trim());
    }

    private String officialLogin(AuthenticatorApplication application) {
        String city = application.getCity().toLowerCase(Locale.ROOT).replace(" ", "");
        return "auth." + city + "@bhumi.gov.in";
    }

    private OfficerView toOfficer(UserAccount user) {
        return new OfficerView(
                user.getId(),
                user.getFullName(),
                user.getEmail(),
                user.getCity(),
                user.getDistrict(),
                user.getState(),
                user.isActive()
        );
    }

    private ApplicationView toApp(AuthenticatorApplication application) {
        return new ApplicationView(
                application.getId(),
                application.getFullName(),
                application.getPersonalEmail(),
                application.getPhone(),
                application.getOfficialIdNumber(),
                application.getCity(),
                application.getDistrict(),
                application.getState(),
                application.getStatus()
        );
    }

    public record Dashboard(
            Long adminId,
            String adminName,
            String stateUnionTerritory,
            String email,
            String phone,
            List<OfficerView> activeAuthenticators,
            List<ApplicationView> pendingApplications,
            List<ApplicationView> rejectedApplications
    ) {}

    public record OfficerView(
            Long id,
            String fullName,
            String officialLogin,
            String city,
            String district,
            String state,
            boolean active
    ) {}

    public record ApplicationView(
            Long id,
            String fullName,
            String personalEmail,
            String phone,
            String officialIdNumber,
            String city,
            String district,
            String state,
            String status
    ) {}
}
