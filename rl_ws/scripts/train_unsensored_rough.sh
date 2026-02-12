#!/bin/bash
docker exec -it isaac-sim bash -c 'cd ~/IsaacLab && \
    ./isaaclab.sh \
    -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task=Isaac-Velocity-Rough-NoSensor-Spot-Micro-v0 \
    --num_envs=16384 \
    --headless'