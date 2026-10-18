package tn.herwell.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import tn.herwell.service.AIServiceClient;

import java.util.Map;

@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class ChatController {
    
    private final AIServiceClient aiServiceClient;
    
    @PostMapping
    public ResponseEntity<Map<String, Object>> chat(@RequestBody Map<String, String> request) {
        String message = request.get("message");
        if (message == null || message.trim().isEmpty()) {
            return ResponseEntity.badRequest().build();
        }
        
        try {
            Map<String, Object> response = aiServiceClient.chat(message, Map.of()).block();
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(503).body(Map.of(
                "error", "AI service unavailable",
                "message", "The AI service is temporarily unavailable. Please try again later."
            ));
        }
    }
    
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        try {
            Map<String, Object> aiHealth = aiServiceClient.health().block();
            return ResponseEntity.ok(Map.of(
                "status", "ok",
                "ai_service", aiHealth
            ));
        } catch (Exception e) {
            return ResponseEntity.status(503).body(Map.of(
                "status", "degraded",
                "ai_service", "unavailable"
            ));
        }
    }
}
