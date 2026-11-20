package com.landregistry.chat;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.landregistry.notify.NotifyService;
import com.landregistry.store.InMemoryAppStore;
import org.junit.jupiter.api.Test;

class ChatServiceTest {

    @Test
    void blocksOffPlatformAndAbuse() {
        InMemoryAppStore store = new InMemoryAppStore();
        ChatService chat = new ChatService(store, new NotifyService(store));
        assertTrue(chat.ethical("Is the plot still available this week?"));
        assertFalse(chat.ethical("Message me on WhatsApp 9876543210"));
        assertFalse(chat.ethical("Pay via UPI and skip registry"));
    }
}
