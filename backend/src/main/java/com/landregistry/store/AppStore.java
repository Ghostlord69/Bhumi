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
import java.util.List;
import java.util.Optional;

public interface AppStore {
    UserAccount saveUser(UserAccount user);

    Optional<UserAccount> user(Long id);

    Optional<UserAccount> userByEmail(String email);

    List<UserAccount> users();

    List<UserAccount> authenticators();

    List<UserAccount> authenticatorsInCity(String city);

    PropertyListing saveProperty(PropertyListing listing);

    Optional<PropertyListing> property(Long id);

    List<PropertyListing> properties();

    AuthenticatorApplication saveApplication(AuthenticatorApplication application);

    Optional<AuthenticatorApplication> application(Long id);

    List<AuthenticatorApplication> applications();

    ChatMessage saveMessage(ChatMessage message);

    List<ChatMessage> messagesForProperty(Long propertyId);

    void audit(Long actorId, String action, String detail);

    List<AuditEvent> audits();

    void putGovernment(GovernmentRecord record);

    Optional<GovernmentRecord> government(String khasra);

    Optional<GovernmentRecord> governmentByUlpin(String ulpin);

    Optional<GovernmentRecord> governmentBySurvey(String surveyNumber);

    List<GovernmentRecord> governmentRecords();

    TransferCertificate saveCertificate(TransferCertificate certificate);

    Optional<TransferCertificate> certificate(Long id);

    Notification saveNotification(Notification notification);

    Optional<Notification> notification(Long id);

    List<Notification> notificationsForUser(Long userId);

    long userCount();

    StateAdmin saveStateAdmin(StateAdmin admin);

    Optional<StateAdmin> stateAdminByUserId(Long userId);

    Optional<StateAdmin> stateAdmin(Long adminId);

    List<StateAdmin> stateAdmins();
}
