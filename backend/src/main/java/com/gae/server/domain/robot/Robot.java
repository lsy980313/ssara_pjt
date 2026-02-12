package com.gae.server.domain.robot;

import com.gae.server.domain.member.Member;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@EntityListeners(AuditingEntityListener.class)
@Table(name = "robot")
public class Robot {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String serialNumber;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private RobotStatus status = RobotStatus.OFFLINE;

    @Column(nullable = false)
    private Integer battery = 100;

    private String location;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "member_id")
    private Member member;

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public Robot(String serialNumber, String name, Member member) {
        this.serialNumber = serialNumber;
        this.name = name;
        this.member = member;
        this.status = RobotStatus.OFFLINE;
        this.battery = 100;
    }

    public void updateName(String name) {
        if (name != null && !name.isBlank()) {
            this.name = name;
        }
    }

    public void updateStatus(RobotStatus status) {
        this.status = status;
    }

    public void updateBattery(Integer battery) {
        if (battery != null && battery >= 0 && battery <= 100) {
            this.battery = battery;
        }
    }

    public void updateLocation(String location) {
        this.location = location;
    }
}
