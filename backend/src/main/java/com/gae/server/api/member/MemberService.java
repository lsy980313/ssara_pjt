package com.gae.server.api.member;

import com.gae.server.api.member.dto.MemberResponse;
import com.gae.server.api.member.dto.MemberUpdateRequest;
import com.gae.server.domain.member.Member;
import com.gae.server.domain.member.MemberRepository;
import com.gae.server.domain.robot.RobotRepository;
import com.gae.server.global.exception.BusinessException;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class MemberService {

    private final MemberRepository memberRepository;
    private final RobotRepository robotRepository;
    private final PasswordEncoder passwordEncoder;

    // 1. 내 정보 조회
    public MemberResponse getMyInfo(String email) {
        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException("로그인 유저 정보가 없습니다."));

        return MemberResponse.from(member);
    }

    // 2. 회원 정보 수정 (이름, 폰번호, 비밀번호)
    @Transactional
    public void updateMember(String email, MemberUpdateRequest request) {
        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException("로그인 유저 정보가 없습니다."));

        if (request.getPassword() != null && !request.getPassword().isBlank()) {
            member.updatePassword(passwordEncoder.encode(request.getPassword()));
        }

        member.updateInfo(request.getName(), request.getPhoneNumber());
    }

    // 3. 회원 탈퇴
    @Transactional
    public void deleteMember(String email) {
        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException("로그인 유저 정보가 없습니다."));

        // 로봇 먼저 삭제
        robotRepository.findByMemberId(member.getId())
                .ifPresent(robotRepository::delete);

        memberRepository.delete(member);
    }
}