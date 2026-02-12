package com.gae.server.api.notification;

import com.gae.server.api.notification.dto.NotificationSettingsDto;
import com.gae.server.api.notification.dto.RegisterTokenRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/notifications")
@RequiredArgsConstructor
public class NotificationController {

    private final NotificationService notificationService;

    /**
     * FCM 토큰 등록/갱신
     */
    @PostMapping("/token")
    public ResponseEntity<String> registerToken(@Valid @RequestBody RegisterTokenRequest request) {
        notificationService.registerToken(request.getFcmToken());
        return ResponseEntity.ok("토큰이 등록되었습니다.");
    }

    /**
     * FCM 토큰 삭제 (알림 비활성화)
     */
    @DeleteMapping("/token")
    public ResponseEntity<String> deleteToken() {
        notificationService.deleteToken();
        return ResponseEntity.ok("토큰이 삭제되었습니다.");
    }

    /**
     * 알림 설정 조회
     */
    @GetMapping("/settings")
    public ResponseEntity<NotificationSettingsDto> getSettings() {
        return ResponseEntity.ok(notificationService.getSettings());
    }

    /**
     * 알림 설정 수정
     */
    @PatchMapping("/settings")
    public ResponseEntity<String> updateSettings(@RequestBody NotificationSettingsDto request) {
        notificationService.updateSettings(request);
        return ResponseEntity.ok("설정이 저장되었습니다.");
    }
}
