package com.landregistry.notify;

import com.landregistry.domain.Notification;
import com.landregistry.security.SecurityUtil;
import java.time.Instant;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/notifications")
public class NotificationController {
    private final NotifyService notifyService;

    public NotificationController(NotifyService notifyService) {
        this.notifyService = notifyService;
    }

    @GetMapping
    public List<NotificationView> mine() {
        Long userId = SecurityUtil.current().id();
        return notifyService.forUser(userId).stream().map(NotificationView::from).toList();
    }

    @PostMapping("/{id}/read")
    public NotificationView read(@PathVariable Long id) {
        return NotificationView.from(notifyService.markRead(SecurityUtil.current().id(), id));
    }

    public record NotificationView(
            Long id,
            String channel,
            String subject,
            String body,
            boolean read,
            Instant createdAt
    ) {
        static NotificationView from(Notification n) {
            return new NotificationView(n.getId(), n.getChannel(), n.getSubject(), n.getBody(), n.isRead(), n.getCreatedAt());
        }
    }
}
