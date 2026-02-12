# 3D printing parts
> 단위 gram

L_arm = 32.8
L_wrist = 26.0
L_arm_cover = 24.1
L_arm_joint = 20
(아래 거 보고 추가)

# ready-made parts
motor = 68.4
jetson = 178.1
astra_pro = 217.4

## mapping mass to links
> urdf에서 front_link, rear_link 길이 수정해야 함
> sim2real 진행 후에 지장 없다면 그냥 쓰기
```
?_foot_link = 26.4 + 68.0 = 94.4
	?_writs + motor
	
?_leg_link = 24.1 + 32.7 + 68.4 = 125.2
	?_arm_cover + ?_arm + motor
	
?_shoulder_link = 20 + 68.4 = 88.4
	?_arm_joint + motor
	
front_link = 59.2 + 53.7 + 16.7 + 217.4 = 346.3
	f_cover + top_modi(long) + sideplate + astra_pro
	
rear_link = 59.4 + 50(추정) + 178.1 + 16.7 + 150(추정) + 214.7 = 668.9
	r_cover + bottom_modi(long) + sideplate + jetson + electronics + battery
위 두개 합쳐서 base_link에 무게 걸어버리는거 가능??
	카메라의 쏠림을 고려하여, front_link 0.3잡고, 나머지 base_link 0.7152에 다 넣음

total = (94.4 + 125.2 + 88.4) * 4 + 346.3 + 668.9 = 2247.2
```
`*`_foot_link 
	

- base_link = 0
- lidar_link = 0
- rear_link
- front_link
- front_left_shoulder_link
- front_left_leg_link_cover
- front_left_leg_link
- front_left_foot_link
- front_left_toe_link
- front_right_shoulder_link
- front_right_leg_link_cover
- front_right_leg_link
	- 
- ???_foot_link: 26.0 + 68.4 
	- ???_wrist + motor
- front_right_toe_link
- rear_left_shoulder_link
- rear_left_leg_link_cover
- rear_left_leg_link
- rear_left_foot_link
- rear_left_toe_link
- rear_right_shoulder_link
- rear_right_leg_link_cover
- rear_right_leg_link
- rear_right_foot_link
- rear_right_toe_link
- imu_link

링크 구조
