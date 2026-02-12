#!/bin/bash
docker exec -it isaac-sim bash -c 'cd ~/IsaacLab && \
    ./isaaclab.sh \
    -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task=Isaac-Velocity-Flat-NoSensor-Spot-Micro-v0 \
    --num_envs=28000 \
    --headless'