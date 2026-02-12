package com.gae.server.api.proxy;

import com.gae.server.api.proxy.dto.GmsChatRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/proxy")
@RequiredArgsConstructor
public class ProxyController {

    private final ProxyService proxyService;

    @PostMapping("/gms/chat")
    public ResponseEntity<Map<String, Object>> gmsChatCompletions(
            @Valid @RequestBody GmsChatRequest request) {
        return ResponseEntity.ok(proxyService.gmsChatCompletions(request));
    }

    @GetMapping("/kakao/geocode")
    public ResponseEntity<Map<String, Object>> kakaoReverseGeocode(
            @RequestParam double lat,
            @RequestParam double lng) {
        return ResponseEntity.ok(proxyService.kakaoReverseGeocode(lat, lng));
    }

    @GetMapping("/kakao/search")
    public ResponseEntity<Map<String, Object>> kakaoKeywordSearch(
            @RequestParam String query,
            @RequestParam double lat,
            @RequestParam double lng,
            @RequestParam(defaultValue = "2000") int radius,
            @RequestParam(defaultValue = "distance") String sort) {
        return ResponseEntity.ok(proxyService.kakaoKeywordSearch(query, lat, lng, radius, sort));
    }
}
