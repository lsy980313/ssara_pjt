package com.gae.server.api.robot;

import com.gae.server.api.robot.dto.RobotResponse;
import com.gae.server.api.robot.dto.RobotUpdateRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/robots")
@RequiredArgsConstructor
public class RobotController {

    private final RobotService robotService;

    @GetMapping("/me")
    public ResponseEntity<RobotResponse> getMyRobot(
            @AuthenticationPrincipal UserDetails userDetails) {
        String email = userDetails.getUsername();
        return ResponseEntity.ok(robotService.getMyRobot(email));
    }

    @PatchMapping("/me")
    public ResponseEntity<RobotResponse> updateMyRobot(
            @AuthenticationPrincipal UserDetails userDetails,
            @RequestBody RobotUpdateRequest request) {
        String email = userDetails.getUsername();
        return ResponseEntity.ok(robotService.updateMyRobot(email, request));
    }
}
