package com.gae.server.api.auth.dto;

import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class FindEmailResponse {
    private String email;        // 마스킹된 이메일
    private String message;
}
