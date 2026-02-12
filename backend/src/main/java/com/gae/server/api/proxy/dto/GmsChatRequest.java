package com.gae.server.api.proxy.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import java.util.List;

public record GmsChatRequest(
        @NotBlank String model,
        @NotEmpty List<Message> messages,
        Integer maxTokens,
        Double temperature
) {
    public record Message(
            @NotBlank String role,
            @NotBlank String content
    ) {}
}
