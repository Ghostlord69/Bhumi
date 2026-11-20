package com.landregistry.store;

import com.landregistry.domain.AuditEvent;
import com.landregistry.domain.AuthenticatorApplication;
import com.landregistry.domain.ChatMessage;
import com.landregistry.domain.GovernmentRecord;
import com.landregistry.domain.Notification;
import com.landregistry.domain.PropertyListing;
import com.landregistry.domain.StateAdmin;
import com.landregistry.domain.TransferCertificate;
import com.landregistry.domain.UserAccount;
import com.landregistry.security.Role;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import org.springframework.context.annotation.Primary;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

/** Default local store — no database required. */
@Component
@Primary
@Profile("!sqlite")
public class InMemoryAppStore implements AppStore {
    private final AtomicLong userSeq = new AtomicLong(100);
    private final AtomicLong propertySeq = new AtomicLong(100);
    private final AtomicLong appSeq = new AtomicLong(100);
    private final AtomicLong chatSeq = new AtomicLong(100);
    private final AtomicLong auditSeq = new AtomicLong(100);
    private final AtomicLong certSeq = new AtomicLong(1000);
    private final AtomicLong notifySeq = new AtomicLong(100);

    private final Map<Long, UserAccount> users = new ConcurrentHashMap<>();
    private final Map<String, UserAccount> usersByEmail = new ConcurrentHashMap<>();
    private final Map<Long, PropertyListing> properties = new ConcurrentHashMap<>();
    private final Map<Long, AuthenticatorApplication> applications = new ConcurrentHashMap<>();
    private final List<ChatMessage> messages = new ArrayList<>();
    private final List<AuditEvent> audits = new ArrayList<>();
    private final Map<String, GovernmentRecord> governmentByKhasra = new ConcurrentHashMap<>();
    private final Map<String, GovernmentRecord> governmentByUlpin = new ConcurrentHashMap<>();
    private final Map<String, GovernmentRecord> governmentBySurvey = new ConcurrentHashMap<>();
    private final Map<Long, TransferCertificate> certificates = new ConcurrentHashMap<>();
    private final Map<Long, Notification> notifications = new ConcurrentHashMap<>();
    private final Map<Long, StateAdmin> stateAdmins = new ConcurrentHashMap<>();
    private final AtomicLong stateAdminSeq = new AtomicLong(100);

    @Override
    public UserAccount saveUser(UserAccount user) {
        if (user.getId() == null) {
            user.setId(userSeq.incrementAndGet());
        }
        users.put(user.getId(), user);
        usersByEmail.put(user.getEmail().toLowerCase(), user);
        return user;
    }

    @Override
    public Optional<UserAccount> user(Long id) {
        return Optional.ofNullable(users.get(id));
    }

    @Override
    public Optional<UserAccount> userByEmail(String email) {
        return Optional.ofNullable(usersByEmail.get(email.toLowerCase()));
    }

    @Override
    public List<UserAccount> users() {
        return new ArrayList<>(users.values());
    }

    @Override
    public List<UserAccount> authenticators() {
        return users.values().stream().filter(u -> u.getRole() == Role.AUTHENTICATOR).toList();
    }

    @Override
    public List<UserAccount> authenticatorsInCity(String city) {
        if (city == null) {
            return List.of();
        }
        return authenticators().stream()
                .filter(UserAccount::isActive)
                .filter(u -> u.getCity() != null && u.getCity().equalsIgnoreCase(city))
                .toList();
    }

    @Override
    public PropertyListing saveProperty(PropertyListing listing) {
        if (listing.getId() == null) {
            listing.setId(propertySeq.incrementAndGet());
        }
        properties.put(listing.getId(), listing);
        return listing;
    }

    @Override
    public Optional<PropertyListing> property(Long id) {
        return Optional.ofNullable(properties.get(id));
    }

    @Override
    public List<PropertyListing> properties() {
        return new ArrayList<>(properties.values());
    }

    @Override
    public AuthenticatorApplication saveApplication(AuthenticatorApplication application) {
        if (application.getId() == null) {
            application.setId(appSeq.incrementAndGet());
        }
        applications.put(application.getId(), application);
        return application;
    }

    @Override
    public Optional<AuthenticatorApplication> application(Long id) {
        return Optional.ofNullable(applications.get(id));
    }

    @Override
    public List<AuthenticatorApplication> applications() {
        return new ArrayList<>(applications.values());
    }

    @Override
    public ChatMessage saveMessage(ChatMessage message) {
        if (message.getId() == null) {
            message.setId(chatSeq.incrementAndGet());
        }
        synchronized (messages) {
            messages.add(message);
        }
        return message;
    }

    @Override
    public List<ChatMessage> messagesForProperty(Long propertyId) {
        synchronized (messages) {
            return messages.stream().filter(m -> propertyId.equals(m.getPropertyId())).toList();
        }
    }

    @Override
    public void audit(Long actorId, String action, String detail) {
        AuditEvent event = new AuditEvent();
        event.setId(auditSeq.incrementAndGet());
        event.setActorId(actorId);
        event.setAction(action);
        event.setDetail(detail);
        synchronized (audits) {
            audits.add(event);
        }
    }

    @Override
    public List<AuditEvent> audits() {
        synchronized (audits) {
            return new ArrayList<>(audits);
        }
    }

    @Override
    public void putGovernment(GovernmentRecord record) {
        if (record.getKhasraNumber() != null && !record.getKhasraNumber().isBlank()) {
            governmentByKhasra.put(record.getKhasraNumber().toLowerCase().trim(), record);
        }
        if (record.getUlpin() != null && !record.getUlpin().isBlank()) {
            governmentByUlpin.put(record.getUlpin().toUpperCase().trim(), record);
        }
        if (record.getSurveyNumber() != null && !record.getSurveyNumber().isBlank()) {
            governmentBySurvey.put(record.getSurveyNumber().toLowerCase().trim(), record);
        }
    }

    @Override
    public Optional<GovernmentRecord> government(String khasra) {
        if (khasra == null) {
            return Optional.empty();
        }
        return Optional.ofNullable(governmentByKhasra.get(khasra.toLowerCase().trim()));
    }

    @Override
    public Optional<GovernmentRecord> governmentByUlpin(String ulpin) {
        if (ulpin == null || ulpin.isBlank()) {
            return Optional.empty();
        }
        return Optional.ofNullable(governmentByUlpin.get(ulpin.toUpperCase().trim()));
    }

    @Override
    public Optional<GovernmentRecord> governmentBySurvey(String surveyNumber) {
        if (surveyNumber == null || surveyNumber.isBlank()) {
            return Optional.empty();
        }
        return Optional.ofNullable(governmentBySurvey.get(surveyNumber.toLowerCase().trim()));
    }

    @Override
    public List<GovernmentRecord> governmentRecords() {
        return new ArrayList<>(governmentByKhasra.values());
    }

    @Override
    public TransferCertificate saveCertificate(TransferCertificate certificate) {
        if (certificate.getId() == null) {
            certificate.setId(certSeq.incrementAndGet());
        }
        certificates.put(certificate.getId(), certificate);
        return certificate;
    }

    @Override
    public Optional<TransferCertificate> certificate(Long id) {
        return Optional.ofNullable(certificates.get(id));
    }

    @Override
    public Notification saveNotification(Notification notification) {
        if (notification.getId() == null) {
            notification.setId(notifySeq.incrementAndGet());
        }
        notifications.put(notification.getId(), notification);
        return notification;
    }

    @Override
    public Optional<Notification> notification(Long id) {
        return Optional.ofNullable(notifications.get(id));
    }

    @Override
    public List<Notification> notificationsForUser(Long userId) {
        return notifications.values().stream()
                .filter(n -> userId.equals(n.getUserId()))
                .sorted(Comparator.comparing(Notification::getCreatedAt).reversed())
                .toList();
    }

    @Override
    public long userCount() {
        return users.size();
    }

    @Override
    public StateAdmin saveStateAdmin(StateAdmin admin) {
        if (admin.getAdminId() == null) {
            admin.setAdminId(stateAdminSeq.incrementAndGet());
        }
        stateAdmins.put(admin.getAdminId(), admin);
        return admin;
    }

    @Override
    public Optional<StateAdmin> stateAdminByUserId(Long userId) {
        return stateAdmins.values().stream().filter(a -> userId.equals(a.getUserId())).findFirst();
    }

    @Override
    public Optional<StateAdmin> stateAdmin(Long adminId) {
        return Optional.ofNullable(stateAdmins.get(adminId));
    }

    @Override
    public List<StateAdmin> stateAdmins() {
        return new ArrayList<>(stateAdmins.values());
    }
}
