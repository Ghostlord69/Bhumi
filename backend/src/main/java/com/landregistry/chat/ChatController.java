package com.landregistry.chat;

import com.landregistry.security.SecurityUtil;
import com.landregistry.store.AppStore;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/chat")
public class ChatController {
    private final ChatService chatService;
    private final AppStore store;

    public ChatController(ChatService chatService, AppStore store) {
        this.chatService = chatService;
        this.store = store;
    }

    @GetMapping("/{propertyId}")
    public List<ChatService.ChatView> thread(@PathVariable Long propertyId) {
        return chatService.thread(SecurityUtil.current(), propertyId).stream()
                .map(m -> ChatService.ChatView.from(m, store))
                .toList();
    }

    @PostMapping("/{propertyId}")
    public ChatService.ChatView send(@PathVariable Long propertyId, @RequestBody SendRequest request) {
        return ChatService.ChatView.from(chatService.send(SecurityUtil.current(), propertyId, request.body()), store);
    }

    public record SendRequest(String body) {}
}
