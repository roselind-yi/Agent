package com.journey.client;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;

public class JourneyAgentClient {
    private final HttpClient client;
    private final String baseUrl;

    public JourneyAgentClient(String baseUrl) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.client = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(5))
                .build();
    }

    public String chat(String message) throws IOException, InterruptedException {
        String payload = "{\"message\":\"" + escapeJson(message) + "\",\"user_id\":\"java-client\"}";
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/chat"))
                .timeout(Duration.ofSeconds(30))
                .header("Content-Type", "application/json; charset=utf-8")
                .POST(HttpRequest.BodyPublishers.ofString(payload, StandardCharsets.UTF_8))
                .build();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
        if (response.statusCode() >= 400) {
            throw new IOException("Agent API returned HTTP " + response.statusCode() + ": " + response.body());
        }
        return response.body();
    }

    private static String escapeJson(String input) {
        StringBuilder builder = new StringBuilder();
        for (char c : input.toCharArray()) {
            switch (c) {
                case '"':
                    builder.append("\\\"");
                    break;
                case '\\':
                    builder.append("\\\\");
                    break;
                case '\n':
                    builder.append("\\n");
                    break;
                case '\r':
                    builder.append("\\r");
                    break;
                case '\t':
                    builder.append("\\t");
                    break;
                default:
                    builder.append(c);
            }
        }
        return builder.toString();
    }

    public static void main(String[] args) throws Exception {
        String question = args.length > 0 ? args[0] : "Explain the RAG and tool-calling highlights of this Agent project.";
        String baseUrl = System.getenv().getOrDefault("JOURNEY_AGENT_BASE_URL", "http://127.0.0.1:8765");
        JourneyAgentClient client = new JourneyAgentClient(baseUrl);
        System.out.println(client.chat(question));
    }
}
