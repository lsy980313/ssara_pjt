docker exec -it isaac-sim bash -c 'cd ~/IsaacLab && \
    ./isaaclab.sh \
    -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task=Isaac-Velocity-Rough-NoSensor-Spot-Micro-Play-v0 \
    --num_envs=50'