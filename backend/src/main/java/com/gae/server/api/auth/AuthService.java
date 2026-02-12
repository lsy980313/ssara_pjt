package com.gae.server.api.auth;

import com.gae.server.api.auth.dto.FindEmailRequest;
import com.gae.server.api.auth.dto.FindEmailResponse;
import com.gae.server.api.auth.dto.LoginRequest;
import com.gae.server.api.auth.dto.ResetPasswordRequest;
import com.gae.server.api.auth.dto.SendTempPasswordRequest;
import com.gae.server.api.auth.dto.SignupRequest;
import com.gae.server.api.auth.dto.TokenResponse;
import java.security.SecureRandom;
import com.gae.server.domain.member.Member;
import com.gae.server.global.exception.BusinessException;
import org.springframework.http.HttpStatus;
import com.gae.server.domain.member.MemberRepository;
import com.gae.server.domain.robot.Robot;
import com.gae.server.domain.robot.RobotRepository;
import com.gae.server.global.jwt.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;
    private final MemberRepository memberRepository;
    private final RobotRepository robotRepository;
    private final PasswordEncoder passwordEncoder;
    private final EmailService emailService;

    // 회원가입
    @Transactional
    public void signup(SignupRequest request) {
        if (memberRepository.findByEmail(request.getEmail()).isPresent()) {
            throw new BusinessException("이미 존재하는 이메일입니다.", HttpStatus.CONFLICT);
        }
        if (robotRepository.existsBySerialNumber(request.getSerialNumber())) {
            throw new BusinessException("이미 등록된 로봇 시리얼 번호입니다.", HttpStatus.CONFLICT);
        }

        Member member = memberRepository.save(Member.builder()
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .name(request.getName())
                .phoneNumber(request.getPhoneNumber())
                .serialNumber(request.getSerialNumber())
                .build());

        // 로봇 자동 생성
        robotRepository.save(Robot.builder()
                .serialNumber(request.getSerialNumber())
                .name(request.getName() + "의 로봇")
                .member(member)
                .build());
    }

    // 로그인
    @Transactional
    public TokenResponse login(LoginRequest request) {
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getEmail(), request.getPassword())
        );
        return jwtTokenProvider.createToken(authentication);
    }

    // 아이디(이메일) 찾기
    @Transactional(readOnly = true)
    public FindEmailResponse findEmail(FindEmailRequest request) {
        Member member = memberRepository.findByNameAndPhoneNumber(request.getName(), request.getPhoneNumber())
                .orElseThrow(() -> new BusinessException("일치하는 회원 정보가 없습니다."));

        return FindEmailResponse.builder()
                .email(member.getEmail())
                .message("가입된 이메일을 찾았습니다.")
                .build();
    }

    // 비밀번호 재설정 (직접 입력 방식)
    @Transactional
    public void resetPassword(ResetPasswordRequest request) {
        Member member = memberRepository.findByEmailAndNameAndPhoneNumber(
                        request.getEmail(), request.getName(), request.getPhoneNumber())
                .orElseThrow(() -> new BusinessException("일치하는 회원 정보가 없습니다."));

        member.updatePassword(passwordEncoder.encode(request.getNewPassword()));
    }

    // 임시 비밀번호 발송 (이메일 방식)
    @Transactional
    public void sendTempPassword(SendTempPasswordRequest request) {
        Member member = memberRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new BusinessException("가입되지 않은 이메일입니다."));

        // 임시 비밀번호 생성 (8자리 영문+숫자)
        String tempPassword = generateTempPassword();

        // DB에 암호화된 임시 비밀번호 저장
        member.updatePassword(passwordEncoder.encode(tempPassword));

        // 이메일 발송
        emailService.sendTempPassword(member.getEmail(), tempPassword);
    }

    // 임시 비밀번호 생성 (12자리)
    private String generateTempPassword() {
        String chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789!@#$%";
        SecureRandom random = new SecureRandom();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 12; i++) {
            sb.append(chars.charAt(random.nextInt(chars.length())));
        }
        return sb.toString();
    }
}