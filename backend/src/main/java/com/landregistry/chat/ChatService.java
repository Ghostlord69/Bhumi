package com.landregistry.chat;

import com.landregistry.common.ApiException;
import com.landregistry.domain.ChatMessage;
import com.landregistry.domain.PropertyListing;
import com.landregistry.domain.PropertyStatus;
import com.landregistry.domain.UserAccount;
import com.landregistry.notify.NotifyService;
import com.landregistry.security.AuthUser;
import com.landregistry.security.Role;
import com.landregistry.store.AppStore;
import java.util.EnumSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.regex.Pattern;
import org.springframework.stereotype.Service;

@Service
public class ChatService {
    private static final Set<String> BLOCKED = Set.of(
            "kill", "hate", "scam", "bribe", "racist", "abuse", "threat", "whatsapp", "upi", "paytm", "gpay"
    );
    private static final Pattern PHONE = Pattern.compile("(\\+91[\\s-]?)?[6-9]\\d{9}");
    private static final EnumSet<PropertyStatus> CHATTABLE = EnumSet.of(
            PropertyStatus.LIVE,
            PropertyStatus.PURCHASE_REQUESTED,
            PropertyStatus.PENDING_TRANSFER
    );

    private final AppStore store;
    private final NotifyService notifyService;

    public ChatService(AppStore store, NotifyService notifyService) {
        this.store = store;
        this.notifyService = notifyService;
    }

    public List<ChatMessage> thread(AuthUser actor, Long propertyId) {
        assertParticipant(actor, propertyId);
        return store.messagesForProperty(propertyId).stream().filter(m -> !m.isBlocked()).toList();
    }

    public ChatMessage send(AuthUser actor, Long propertyId, String body) {
        if (actor.role() != Role.USER) {
            throw new ApiException(403, "Chat is for signed-in users");
        }
        PropertyListing listing = assertParticipant(actor, propertyId);
        if (!CHATTABLE.contains(listing.getStatus())) {
            throw new ApiException(400, "Chat is available while the listing is live or in purchase progress");
        }
        ChatMessage message = new ChatMessage();
        message.setPropertyId(propertyId);
        message.setSenderId(actor.id());
        message.setBody(body);
        message.setBlocked(!ethical(body));
        if (message.isBlocked()) {
            throw new ApiException(400, "Message blocked: keep chat respectful and on this app. Do not share phone numbers or off-platform payments.");
        }
        ChatMessage saved = store.saveMessage(message);

        Long counterpartId = actor.id().equals(listing.getSellerId())
                ? listing.getBuyerId()
                : listing.getSellerId();
        if (counterpartId == null && !actor.id().equals(listing.getSellerId())) {
            counterpartId = listing.getSellerId();
        }
        if (counterpartId != null) {
            store.user(counterpartId).ifPresent(user ->
                    notifyService.notifyUser(
                            user,
                            "New chat message",
                            store.user(actor.id()).map(UserAccount::getFullName).orElse("Someone")
                                    + " on property #" + propertyId + ": " + body
                    ));
        }
        return saved;
    }

    private PropertyListing assertParticipant(AuthUser actor, Long propertyId) {
        PropertyListing listing = store.property(propertyId).orElseThrow(() -> new ApiException(404, "Property not found"));
        boolean seller = actor.id().equals(listing.getSellerId());
        boolean buyerSide = actor.role() == Role.USER
                && !seller
                && (listing.getBuyerId() == null
                || actor.id().equals(listing.getBuyerId())
                || listing.getStatus() == PropertyStatus.LIVE);
        if (!seller && !buyerSide) {
            throw new ApiException(403, "You cannot open this conversation");
        }
        return listing;
    }

    boolean ethical(String body) {
        if (body == null || body.isBlank()) {
            return false;
        }
        String lower = body.toLowerCase(Locale.ROOT);
        if (PHONE.matcher(body).find()) {
            return false;
        }
        return BLOCKED.stream().noneMatch(lower::contains);
    }

    public record ChatView(Long id, Long senderId, String senderName, String body, java.time.Instant createdAt) {
        static ChatView from(ChatMessage message, AppStore store) {
            String name = store.user(message.getSenderId()).map(UserAccount::getFullName).orElse("User");
            return new ChatView(message.getId(), message.getSenderId(), name, message.getBody(), message.getCreatedAt());
        }
    }
}
