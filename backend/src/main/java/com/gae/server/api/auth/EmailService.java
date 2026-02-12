package com.gae.server.api.auth;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;
import com.gae.server.global.exception.BusinessException;
import org.springframework.http.HttpStatus;

@Slf4j
@Service
@RequiredArgsConstructor
public class EmailService {

    private final JavaMailSender mailSender;

    /**
     * 임시 비밀번호 이메일 발송
     */
    public void sendTempPassword(String toEmail, String tempPassword) {
        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(toEmail);
        message.setSubject("[파트라슈 봇] 임시 비밀번호 안내");
        message.setText(
                "안녕하세요, 파트라슈 봇입니다.\n\n" +
                "요청하신 임시 비밀번호를 안내해 드립니다.\n\n" +
                "━━━━━━━━━━━━━━━━━━━━\n" +
                "임시 비밀번호: " + tempPassword + "\n" +
                "━━━━━━━━━━━━━━━━━━━━\n\n" +
                "로그인 후 반드시 비밀번호를 변경해 주세요.\n\n" +
                "감사합니다."
        );

        try {
            mailSender.send(message);
            log.info("임시 비밀번호 이메일 발송 완료: {}", maskEmail(toEmail));
        } catch (Exception e) {
            log.error("이메일 발송 실패: {}", e.getMessage());
            throw new BusinessException("이메일 발송에 실패했습니다.", HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    private String maskEmail(String email) {
        if (email == null || !email.contains("@")) {
            return "***";
        }
        String[] parts = email.split("@");
        String local = parts[0];
        if (local.length() <= 2) {
            return "**@" + parts[1];
        }
        return local.substring(0, 2) + "***@" + parts[1];
    }
}
