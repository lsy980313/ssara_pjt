package com.gae.server.api.robot;

import com.gae.server.api.robot.dto.RobotResponse;
import com.gae.server.api.robot.dto.RobotUpdateRequest;
import com.gae.server.domain.member.Member;
import com.gae.server.domain.member.MemberRepository;
import com.gae.server.domain.robot.Robot;
import com.gae.server.domain.robot.RobotRepository;
import com.gae.server.global.exception.BusinessException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class RobotService {

    private final RobotRepository robotRepository;
    private final MemberRepository memberRepository;

    public RobotResponse getMyRobot(String email) {
        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException("로그인 유저 정보가 없습니다."));

        Robot robot = robotRepository.findByMemberId(member.getId())
                .orElseThrow(() -> new BusinessException("등록된 로봇이 없습니다."));

        return RobotResponse.from(robot);
    }

    @Transactional
    public RobotResponse updateMyRobot(String email, RobotUpdateRequest request) {
        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException("로그인 유저 정보가 없습니다."));

        Robot robot = robotRepository.findByMemberId(member.getId())
                .orElseThrow(() -> new BusinessException("등록된 로봇이 없습니다."));

        if (request.name() != null) {
            robot.updateName(request.name());
        }
        if (request.status() != null) {
            robot.updateStatus(request.status());
        }
        if (request.battery() != null) {
            robot.updateBattery(request.battery());
        }
        if (request.location() != null) {
            robot.updateLocation(request.location());
        }

        return RobotResponse.from(robot);
    }
}
