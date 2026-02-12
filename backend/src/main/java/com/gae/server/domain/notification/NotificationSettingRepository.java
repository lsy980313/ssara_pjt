package com.gae.server.domain.notification;

import com.gae.server.domain.member.Member;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface NotificationSettingRepository extends JpaRepository<NotificationSetting, Long> {

    Optional<NotificationSetting> findByMember(Member member);

    Optional<NotificationSetting> findByMemberId(Long memberId);
}
