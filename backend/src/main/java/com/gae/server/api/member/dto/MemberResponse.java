package com.gae.server.api.member.dto;

import com.gae.server.domain.member.Member;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class MemberResponse {
    private Long id;
    private String email;
    private String name;
    private String phoneNumber;
    private String role;

    // Member 엔티티를 DTO로 변환하는 메서드
    public static MemberResponse from(Member member) {
        return MemberResponse.builder()
                .id(member.getId())
                .email(member.getEmail())
                .name(member.getName())
                .phoneNumber(member.getPhoneNumber())
                .role(member.getRole())
                .build();
    }
}