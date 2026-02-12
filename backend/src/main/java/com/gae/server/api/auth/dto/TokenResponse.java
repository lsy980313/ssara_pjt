package com.gae.server.api.auth.dto;

import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class TokenResponse {
    private String grantType;
    private String accessToken;
    private Long accessTokenExpiresAt;
}