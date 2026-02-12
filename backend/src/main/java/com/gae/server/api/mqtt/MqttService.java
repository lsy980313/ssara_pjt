package com.gae.server.api.mqtt;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gae.server.api.robot.dto.ros.RosMessage;
import com.gae.server.api.robot.dto.ros.Twist;
import com.gae.server.domain.activity.ActivityLog;
import com.gae.server.domain.activity.ActivityLogRepository;
import com.gae.server.domain.robot.Robot;
import com.gae.server.domain.robot.RobotRepository;
import com.gae.server.domain.robot.RobotStatus;
import com.gae.server.global.exception.BusinessException;
import org.springframework.http.HttpStatus;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.integration.annotation.ServiceActivator;
import org.springframework.messaging.Message;
import org.springframework.messaging.MessageHeaders;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class MqttService {

    private static final String TOPIC_HEADER = "mqtt_receivedTopic";
    private static final String TOPIC_CMD_VEL = "robot/cmd/vel";
    private static final String TEST_ROBOT_SN = "TEST-ROBOT-001";

    private final SimpMessagingTemplate messagingTemplate;
    private final MqttGateway mqttGateway;
    private final ObjectMapper objectMapper;
    private final RobotRepository robotRepository;
    private final ActivityLogRepository activityLogRepository;

    @ServiceActivator(inputChannel = "mqttInputChannel")
    @Transactional
    public void handleMessage(Message<?> message) {
        MessageHeaders headers = message.getHeaders();
        String topic = (String) headers.get(TOPIC_HEADER);
        String payload = message.getPayload().toString();

        log.info("MQTT [{}] -> {}", topic, payload);

        // MQTT 토픽을 WebSocket 토픽으로 변환하여 브로드캐스트 + DB 저장
        switch (topic) {
            case "robot/status" -> {
                messagingTemplate.convertAndSend("/topic/robot/status", payload);
                updateRobotStatus(payload);
            }
            case "robot/pose" -> {
                messagingTemplate.convertAndSend("/topic/robot/pose", payload);
                updateRobotPose(payload);
            }
            case "robot/map" -> {
                messagingTemplate.convertAndSend("/topic/robot/map", payload);
            }
            case "robot/activity" -> {
                messagingTemplate.convertAndSend("/topic/robot/activity", payload);
                saveActivityLog(payload);
                log.info("Activity event saved: {}", payload);
            }
            case "robot/summary" -> {
                messagingTemplate.convertAndSend("/topic/robot/summary", payload);
                log.info("Daily summary: {}", payload);
            }
            default -> log.warn("Unknown MQTT topic: {}", topic);
        }
    }

    /**
     * 로봇 상태 업데이트 (battery, state)
     */
    private void updateRobotStatus(String payload) {
        try {
            JsonNode json = objectMapper.readTree(payload);
            Robot robot = robotRepository.findBySerialNumber(TEST_ROBOT_SN).orElse(null);
            if (robot == null) {
                log.warn("Robot not found: {}", TEST_ROBOT_SN);
                return;
            }

            if (json.has("battery")) {
                robot.updateBattery(json.get("battery").asInt());
            }
            if (json.has("isOnline")) {
                RobotStatus status = json.get("isOnline").asBoolean()
                    ? RobotStatus.ONLINE : RobotStatus.OFFLINE;
                robot.updateStatus(status);
            }
            robotRepository.save(robot);
            log.info("Robot status updated: battery={}, status={}", robot.getBattery(), robot.getStatus());
        } catch (Exception e) {
            log.error("Failed to update robot status", e);
        }
    }

    /**
     * 로봇 위치 업데이트
     */
    private void updateRobotPose(String payload) {
        try {
            JsonNode json = objectMapper.readTree(payload);
            Robot robot = robotRepository.findBySerialNumber(TEST_ROBOT_SN).orElse(null);
            if (robot == null) return;

            double x = json.has("x") ? json.get("x").asDouble() : 0;
            double y = json.has("y") ? json.get("y").asDouble() : 0;
            robot.updateLocation(String.format("(%.2f, %.2f)", x, y));

            if (json.has("state")) {
                String state = json.get("state").asText();
                RobotStatus status = "active".equals(state) ? RobotStatus.ONLINE : RobotStatus.OFFLINE;
                robot.updateStatus(status);
            }

            robotRepository.save(robot);
            log.info("Robot pose updated: location={}, status={}", robot.getLocation(), robot.getStatus());
        } catch (Exception e) {
            log.error("Failed to update robot pose", e);
        }
    }

    /**
     * 활동 로그 저장
     */
    private void saveActivityLog(String payload) {
        try {
            JsonNode json = objectMapper.readTree(payload);
            Robot robot = robotRepository.findBySerialNumber(TEST_ROBOT_SN).orElse(null);
            if (robot == null) return;

            String severity = json.has("severity") ? json.get("severity").asText() : "LOW";
            String msg = json.has("message") ? json.get("message").asText() : "Unknown event";

            ActivityLog.ActivityType activityType = "HIGH".equals(severity)
                ? ActivityLog.ActivityType.WARNING
                : ActivityLog.ActivityType.INFO;

            ActivityLog activityLog = ActivityLog.builder()
                .robot(robot)
                .type(activityType)
                .message(msg)
                .detail(severity)
                .build();

            activityLogRepository.save(activityLog);
            log.info("Activity log saved: type={}, message={}", activityType, msg);
        } catch (Exception e) {
            log.error("Failed to save activity log", e);
        }
    }

    /**
     * Rosbridge Protocol 형식으로 로봇 속도 명령 전송
     * @param linearX 전진(+)/후진(-) 속도
     * @param angularZ 좌회전(+)/우회전(-) 각속도
     */
    public void sendVelocity(double linearX, double angularZ) {
        Twist twist = Twist.of(linearX, angularZ);
        RosMessage<Twist> rosMessage = RosMessage.cmdVel(twist);

        try {
            String payload = objectMapper.writeValueAsString(rosMessage);
            mqttGateway.sendToMqtt(payload, TOPIC_CMD_VEL);
            log.info("Velocity command sent: [{}] -> {}", TOPIC_CMD_VEL, payload);
        } catch (JsonProcessingException e) {
            log.error("Failed to serialize ROS message", e);
            throw new BusinessException("속도 명령 전송에 실패했습니다.", HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    /**
     * 로봇 정지 명령 전송
     */
    public void sendStop() {
        sendVelocity(0.0, 0.0);
    }
}
