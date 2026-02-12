package com.gae.server.api.activity.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DailySummaryDto {

    private int totalEvents;
    private int walkTime;    // 분 단위
    private double distance; // km 단위
    private int alerts;      // 경고 개수
}
