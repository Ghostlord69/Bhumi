package com.landregistry.ai;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.landregistry.domain.StoredFile;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Optional;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class AiClient {
    private static final Logger log = LoggerFactory.getLogger(AiClient.class);

    private final String baseUrl;
    private final ObjectMapper mapper;
    private final HttpClient http = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(3))
            .build();

    public AiClient(@Value("${app.ai.base-url:http://localhost:8000}") String baseUrl, ObjectMapper mapper) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.mapper = mapper;
    }

    public Optional<ExtractionResult> extract(StoredFile paper) {
        if (paper == null || paper.getBytes() == null || paper.getBytes().length == 0) {
            return Optional.empty();
        }
        try {
            String boundary = "----BhumiBoundary" + UUID.randomUUID();
            String filename = paper.getOriginalName() == null ? "paper.png" : paper.getOriginalName();
            String contentType = paper.getContentType() == null ? "application/octet-stream" : paper.getContentType();

            byte[] preamble = (
                    "--" + boundary + "\r\n"
                            + "Content-Disposition: form-data; name=\"file\"; filename=\"" + filename + "\"\r\n"
                            + "Content-Type: " + contentType + "\r\n\r\n"
            ).getBytes();
            byte[] closing = ("\r\n--" + boundary + "--\r\n").getBytes();
            byte[] body = new byte[preamble.length + paper.getBytes().length + closing.length];
            System.arraycopy(preamble, 0, body, 0, preamble.length);
            System.arraycopy(paper.getBytes(), 0, body, preamble.length, paper.getBytes().length);
            System.arraycopy(closing, 0, body, preamble.length + paper.getBytes().length, closing.length);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/extract"))
                    .timeout(Duration.ofSeconds(45))
                    .header("Content-Type", "multipart/form-data; boundary=" + boundary)
                    .POST(HttpRequest.BodyPublishers.ofByteArray(body))
                    .build();
            HttpResponse<String> response = http.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                log.warn("AI extract HTTP {}", response.statusCode());
                return Optional.empty();
            }
            JsonNode node = mapper.readTree(response.body());
            return Optional.of(new ExtractionResult(
                    text(node, "ulpin"),
                    text(node, "ownerName"),
                    text(node, "khasraNumber"),
                    text(node, "surveyNumber"),
                    text(node, "khataNumber"),
                    text(node, "khewatNumber"),
                    text(node, "khatauniNumber"),
                    text(node, "parcelIdType"),
                    text(node, "matchTier"),
                    text(node, "village"),
                    text(node, "tehsil"),
                    text(node, "district"),
                    text(node, "state"),
                    node.path("areaAcres").isNumber() ? node.path("areaAcres").asDouble() : null,
                    text(node, "landType"),
                    node.path("confidence").asDouble(0),
                    text(node, "note"),
                    node.path("latitude").isNumber() ? node.path("latitude").asDouble() : null,
                    node.path("longitude").isNumber() ? node.path("longitude").asDouble() : null,
                    text(node, "locateUrl")
            ));
        } catch (Exception ex) {
            log.warn("AI extract unavailable: {}", ex.toString());
            return Optional.empty();
        }
    }

    private String text(JsonNode node, String field) {
        JsonNode value = node.get(field);
        if (value == null || value.isNull()) {
            return null;
        }
        String text = value.asText();
        return text == null || text.isBlank() || "null".equalsIgnoreCase(text) ? null : text.trim();
    }

    public record ExtractionResult(
            String ulpin,
            String ownerName,
            String khasraNumber,
            String surveyNumber,
            String khataNumber,
            String khewatNumber,
            String khatauniNumber,
            String parcelIdType,
            String matchTier,
            String village,
            String tehsil,
            String district,
            String state,
            Double areaAcres,
            String landType,
            double confidence,
            String note,
            Double latitude,
            Double longitude,
            String locateUrl
    ) {}
}
