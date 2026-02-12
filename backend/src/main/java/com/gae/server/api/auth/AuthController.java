package com.gae.server.api.auth;

import com.gae.server.api.auth.dto.FindEmailRequest;
import com.gae.server.api.auth.dto.FindEmailResponse;
import com.gae.server.api.auth.dto.LoginRequest;
import com.gae.server.api.auth.dto.ResetPasswordRequest;
import com.gae.server.api.auth.dto.SendTempPasswordRequest;
import com.gae.server.api.auth.dto.SignupRequest;
import com.gae.server.api.auth.dto.TokenResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    // 회원가입 API
    @PostMapping("/signup")
    public ResponseEntity<String> signup(@Valid @RequestBody SignupRequest request) {
        authService.signup(request);
        return ResponseEntity.ok("가입 완료!");
    }

    // 로그인 API
    @PostMapping("/login")
    public ResponseEntity<TokenResponse> login(@Valid @RequestBody LoginRequest request) {
        return ResponseEntity.ok(authService.login(request));
    }

    // 아이디(이메일) 찾기 API
    @PostMapping("/find-email")
    public ResponseEntity<FindEmailResponse> findEmail(@Valid @RequestBody FindEmailRequest request) {
        return ResponseEntity.ok(authService.findEmail(request));
    }

    // 비밀번호 재설정 API (직접 입력 방식)
    @PostMapping("/reset-password")
    public ResponseEntity<String> resetPassword(@Valid @RequestBody ResetPasswordRequest request) {
        authService.resetPassword(request);
        return ResponseEntity.ok("비밀번호가 변경되었습니다.");
    }

    // 임시 비밀번호 발송 API (이메일 방식)
    @PostMapping("/send-temp-password")
    public ResponseEntity<String> sendTempPassword(@Valid @RequestBody SendTempPasswordRequest request) {
        authService.sendTempPassword(request);
        return ResponseEntity.ok("임시 비밀번호가 이메일로 발송되었습니다.");
    }
}