package com.gae.server.global.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class RateLimitFilter extends OncePerRequestFilter {

    private static final int MAX_REQUESTS = 10;
    private static final long WINDOW_MS = 60_000; // 1분
    private static final int EVICTION_THRESHOLD = 1000;

    private final ConcurrentHashMap<String, RequestCounter> requestCounts = new ConcurrentHashMap<>();

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        String path = request.getRequestURI();

        // 인증 관련 엔드포인트만 Rate Limit 적용
        if (path.startsWith("/api/auth/")) {
            String clientIp = request.getRemoteAddr();
            String key = clientIp + ":" + path;

            if (requestCounts.size() > EVICTION_THRESHOLD) {
                evictExpiredEntries();
            }

            RequestCounter counter = requestCounts.compute(key, (k, existing) -> {
                long now = System.currentTimeMillis();
                if (existing == null || now - existing.windowStart > WINDOW_MS) {
                    return new RequestCounter(now);
                }
                existing.count.incrementAndGet();
                return existing;
            });

            if (counter.count.get() > MAX_REQUESTS) {
                response.setStatus(429);
                response.setContentType("application/json;charset=UTF-8");
                response.getWriter().write("{\"error\": \"요청이 너무 많습니다. 잠시 후 다시 시도해주세요.\"}");
                return;
            }
        }

        filterChain.doFilter(request, response);
    }

    private void evictExpiredEntries() {
        long now = System.currentTimeMillis();
        requestCounts.entrySet().removeIf(entry -> now - entry.getValue().windowStart > WINDOW_MS);
    }

    private static class RequestCounter {
        final long windowStart;
        final AtomicInteger count;

        RequestCounter(long windowStart) {
            this.windowStart = windowStart;
            this.count = new AtomicInteger(1);
        }
    }
}
