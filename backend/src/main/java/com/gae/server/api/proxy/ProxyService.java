package com.gae.server.api.proxy;

import com.gae.server.api.proxy.dto.GmsChatRequest;
import com.gae.server.global.exception.BusinessException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class ProxyService {

    private final RestTemplate restTemplate;

    @Value("${external.gms.api-key}")
    private String gmsApiKey;

    @Value("${external.gms.base-url}")
    private String gmsBaseUrl;

    @Value("${external.kakao.rest-api-key}")
    private String kakaoRestApiKey;

    @Value("${external.kakao.base-url}")
    private String kakaoBaseUrl;

    /**
     * GMS (OpenAI proxy) chat completions
     */
    public Map<String, Object> gmsChatCompletions(GmsChatRequest request) {
        String url = gmsBaseUrl + "/chat/completions";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBearerAuth(gmsApiKey);

        Map<String, Object> body = new HashMap<>();
        body.put("model", request.model());
        body.put("messages", request.messages());
        if (request.maxTokens() != null) body.put("max_tokens", request.maxTokens());
        if (request.temperature() != null) body.put("temperature", request.temperature());

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);

        try {
            ResponseEntity<Map> response = restTemplate.exchange(
                    url, HttpMethod.POST, entity, Map.class
            );
            return response.getBody();
        } catch (RestClientException e) {
            log.error("GMS API 호출 실패: {}", e.getMessage());
            throw new BusinessException("AI 서비스 호출에 실패했습니다.", HttpStatus.BAD_GATEWAY);
        }
    }

    /**
     * 카카오 역지오코딩: 좌표 → 주소
     */
    public Map<String, Object> kakaoReverseGeocode(double lat, double lng) {
        String url = UriComponentsBuilder
                .fromHttpUrl(kakaoBaseUrl + "/geo/coord2address.json")
                .queryParam("x", lng)
                .queryParam("y", lat)
                .toUriString();

        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "KakaoAK " + kakaoRestApiKey);

        HttpEntity<Void> entity = new HttpEntity<>(headers);

        try {
            ResponseEntity<Map> response = restTemplate.exchange(
                    url, HttpMethod.GET, entity, Map.class
            );
            return response.getBody();
        } catch (RestClientException e) {
            log.error("카카오 역지오코딩 API 호출 실패: {}", e.getMessage());
            throw new BusinessException("위치 조회에 실패했습니다.", HttpStatus.BAD_GATEWAY);
        }
    }

    /**
     * 카카오 키워드 장소 검색
     */
    public Map<String, Object> kakaoKeywordSearch(String query, double lat, double lng,
                                                   int radius, String sort) {
        String url = UriComponentsBuilder
                .fromHttpUrl(kakaoBaseUrl + "/search/keyword.json")
                .queryParam("query", query)
                .queryParam("y", lat)
                .queryParam("x", lng)
                .queryParam("radius", radius)
                .queryParam("sort", sort)
                .toUriString();

        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "KakaoAK " + kakaoRestApiKey);

        HttpEntity<Void> entity = new HttpEntity<>(headers);

        try {
            ResponseEntity<Map> response = restTemplate.exchange(
                    url, HttpMethod.GET, entity, Map.class
            );
            return response.getBody();
        } catch (RestClientException e) {
            log.error("카카오 장소 검색 API 호출 실패: {}", e.getMessage());
            throw new BusinessException("장소 검색에 실패했습니다.", HttpStatus.BAD_GATEWAY);
        }
    }
}
