package tn.herwell.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.time.Duration;
import java.util.Map;

@Service
public class AIServiceClient {
    
    private final WebClient webClient;
    
    public AIServiceClient(@Value("${ai.service.url}") String aiServiceUrl) {
        this.webClient = WebClient.builder()
            .baseUrl(aiServiceUrl)
            .build();
    }
    
    public Mono<Map<String, Object>> chat(String message, Map<String, Object> context) {
        return webClient.post()
            .uri("/api/chat")
            .bodyValue(Map.of("message", message, "context", context))
            .retrieve()
            .bodyToMono(Map.class)
            .timeout(Duration.ofSeconds(30));
    }
    
    public Mono<Map<String, Object>> health() {
        return webClient.get()
            .uri("/health")
            .retrieve()
            .bodyToMono(Map.class)
            .timeout(Duration.ofSeconds(5));
    }
}
