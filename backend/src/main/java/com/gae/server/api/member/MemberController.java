package com.gae.server.api.member;

import com.gae.server.api.member.dto.MemberResponse;
import com.gae.server.api.member.dto.MemberUpdateRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/members")
@RequiredArgsConstructor
public class MemberController {

    private final MemberService memberService;

    // 1. 내 정보 조회
    @GetMapping("/me")
    public ResponseEntity<MemberResponse> getMyInfo(@AuthenticationPrincipal UserDetails userDetails) {
        MemberResponse response = memberService.getMyInfo(userDetails.getUsername());
        return ResponseEntity.ok(response);
    }

    // 2. 내 정보 수정 (PATCH)
    @PatchMapping("/me")
    public ResponseEntity<String> updateMember(
            @AuthenticationPrincipal UserDetails userDetails,
            @Valid @RequestBody MemberUpdateRequest request) {

        memberService.updateMember(userDetails.getUsername(), request);
        return ResponseEntity.ok("회원 정보가 수정되었습니다.");
    }

    // 3. 회원 탈퇴 (DELETE)
    @DeleteMapping("/me")
    public ResponseEntity<String> deleteMember(@AuthenticationPrincipal UserDetails userDetails) {

        memberService.deleteMember(userDetails.getUsername());
        return ResponseEntity.ok("회원 탈퇴가 완료되었습니다.");
    }
}