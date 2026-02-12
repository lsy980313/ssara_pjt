#!/bin/bash
xhost +local:

docker run --name isaac-sim \
    --entrypoint bash \
    -it \
    --gpus all \
    -e "ACCEPT_EULA=Y" \
    --network=host \
    -u 1234:1234 \
    -e "PRIVACY_CONSENT=Y" \
    -v "$HOME/.Xauthority:/isaac-sim/.Xauthority" \
    -e DISPLAY \
    -e "ROS_DISTRO=humble" \
    -e "RMW_IMPLEMENTATION=rmw_fastrtps_cpp" \
    -e "LD_LIBRARY_PATH=/isaac-sim/exts/isaacsim.ros2.bridge/humble/lib" \
    -e "ROS_DOMAIN_ID=0" \
    -v /etc/localtime:/etc/localtime:ro \
    -v /etc/timezone:/etc/timezone:ro \
    -v ~/docker/isaac-sim/cache/main:/isaac-sim/.cache:rw \
    -v ~/docker/isaac-sim/cache/computecache:/isaac-sim/.nv/ComputeCache:rw \
    -v ~/docker/isaac-sim/logs:/isaac-sim/.nvidia-omniverse/logs:rw \
    -v ~/docker/isaac-sim/config:/isaac-sim/.nvidia-omniverse/config:rw \
    -v ~/docker/isaac-sim/data:/isaac-sim/.local/share/ov/data:rw \
    -v ~/docker/isaac-sim/pkg:/isaac-sim/.local/share/ov/pkg:rw \
    $(: 'Bind additional Mounts') \
    -v /home/actuating/workspaces/spotmicro/data/usd:/isaac-sim/data/usd:rw \
    -v /home/actuating/workspaces/spotmicro/data/train_myrobot/config:/isaac-sim/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config:rw \
    -v /home/actuating/workspaces/spotmicro/logs:/isaac-sim/IsaacLab/logs:rw \
    isaac-sim-img