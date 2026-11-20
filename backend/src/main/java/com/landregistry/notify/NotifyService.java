package com.landregistry.notify;

import com.landregistry.domain.Notification;
import com.landregistry.domain.UserAccount;
import com.landregistry.store.AppStore;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class NotifyService {
    private static final Logger log = LoggerFactory.getLogger(NotifyService.class);
    private final AppStore store;

    public NotifyService(AppStore store) {
        this.store = store;
    }

    public void email(String to, String subject, String body) {
        log.info("EMAIL to={} subject={} body={}", to, subject, body);
        store.userByEmail(to).ifPresent(user -> persist(user.getId(), "EMAIL", subject, body));
    }

    public void sms(String phone, String body) {
        log.info("SMS to={} body={}", phone, body);
        store.users().stream()
                .filter(u -> phone != null && phone.equals(u.getPhone()))
                .findFirst()
                .ifPresent(user -> persist(user.getId(), "SMS", "SMS notification", body));
    }

    public void notifyUser(UserAccount user, String subject, String body) {
        if (user == null) {
            return;
        }
        persist(user.getId(), "IN_APP", subject, body);
        if (user.getEmail() != null) {
            log.info("EMAIL to={} subject={} body={}", user.getEmail(), subject, body);
            persist(user.getId(), "EMAIL", subject, body);
        }
        if (user.getPhone() != null) {
            log.info("SMS to={} body={}", user.getPhone(), body);
            persist(user.getId(), "SMS", subject, body);
        }
    }

    public void notifyCityAuthenticators(String city, String subject, String body) {
        for (UserAccount officer : store.authenticatorsInCity(city)) {
            notifyUser(officer, subject, body);
        }
    }

    public List<Notification> forUser(Long userId) {
        return store.notificationsForUser(userId);
    }

    public Notification markRead(Long userId, Long notificationId) {
        Notification notification = store.notification(notificationId)
                .orElseThrow(() -> new com.landregistry.common.ApiException(404, "Notification not found"));
        if (!userId.equals(notification.getUserId())) {
            throw new com.landregistry.common.ApiException(403, "Not your notification");
        }
        notification.setRead(true);
        return store.saveNotification(notification);
    }

    private void persist(Long userId, String channel, String subject, String body) {
        Notification notification = new Notification();
        notification.setUserId(userId);
        notification.setChannel(channel);
        notification.setSubject(subject);
        notification.setBody(body);
        notification.setRead(false);
        store.saveNotification(notification);
    }
}
