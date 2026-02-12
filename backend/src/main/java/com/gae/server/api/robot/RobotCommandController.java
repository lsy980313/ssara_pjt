package com.gae.server.api.robot;

import com.gae.server.api.mqtt.MqttGateway;
import com.gae.server.api.mqtt.MqttService;
import com.gae.server.api.robot.dto.NavRequest;
import com.gae.server.api.robot.dto.VelocityRequest;
import com.gae.server.domain.member.Member;
import com.gae.server.domain.member.MemberRepository;
import com.gae.server.domain.robot.RobotRepository;
import com.gae.server.global.exception.BusinessException;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/robot")
@RequiredArgsConstructor
public class RobotCommandController {

    private final MqttGateway mqttGateway;
    private final MqttService mqttService;
    private final MemberRepository memberRepository;
    private final RobotRepository robotRepository;

    private static final String TOPIC_CMD_MOVE = "robot/cmd/move";
    private static final String TOPIC_CMD_NAV = "robot/cmd/nav";

    @PostMapping("/home")
    public ResponseEntity<Map<String, String>> goHome(@AuthenticationPrincipal UserDetails userDetails) {
        verifyRobotOwner(userDetails.getUsername());

        String payload = "{\"action\": \"home\"}";
        mqttGateway.sendToMqtt(payload, TOPIC_CMD_MOVE);

        log.info("Command sent: [{}] -> {}", TOPIC_CMD_MOVE, payload);
        return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "Home command sent",
                "topic", TOPIC_CMD_MOVE
        ));
    }

    @PostMapping("/stop")
    public ResponseEntity<Map<String, String>> stop(@AuthenticationPrincipal UserDetails userDetails) {
        verifyRobotOwner(userDetails.getUsername());

        String payload = "{\"action\": \"stop\"}";
        mqttGateway.sendToMqtt(payload, TOPIC_CMD_MOVE);

        log.info("Command sent: [{}] -> {}", TOPIC_CMD_MOVE, payload);
        return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "Stop command sent",
                "topic", TOPIC_CMD_MOVE
        ));
    }

    @PostMapping("/nav")
    public ResponseEntity<Map<String, String>> navigate(
            @AuthenticationPrincipal UserDetails userDetails,
            @Valid @RequestBody NavRequest request) {
        verifyRobotOwner(userDetails.getUsername());

        String payload = String.format("{\"x\": %s, \"y\": %s}", request.x(), request.y());
        mqttGateway.sendToMqtt(payload, TOPIC_CMD_NAV);

        log.info("Command sent: [{}] -> {}", TOPIC_CMD_NAV, payload);
        return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "Navigation command sent",
                "topic", TOPIC_CMD_NAV,
                "target", String.format("x=%s, y=%s", request.x(), request.y())
        ));
    }

    /**
     * 로봇 속도 제어 (조이스틱/화살표 키 조작용)
     * Rosbridge Protocol 형식으로 MQTT 전송
     */
    @PostMapping("/control")
    public ResponseEntity<Map<String, Object>> control(
            @AuthenticationPrincipal UserDetails userDetails,
            @Valid @RequestBody VelocityRequest request) {
        verifyRobotOwner(userDetails.getUsername());

        mqttService.sendVelocity(request.linearX(), request.angularZ());

        log.info("Velocity command: linearX={}, angularZ={}", request.linearX(), request.angularZ());
        return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "Velocity command sent",
                "linearX", request.linearX(),
                "angularZ", request.angularZ()
        ));
    }

    private void verifyRobotOwner(String email) {
        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException("회원 정보를 찾을 수 없습니다."));
        robotRepository.findByMemberId(member.getId())
                .orElseThrow(() -> new BusinessException("등록된 로봇이 없습니다.", HttpStatus.FORBIDDEN));
    }
}
