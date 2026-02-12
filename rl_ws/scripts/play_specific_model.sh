docker exec -it isaac-sim bash -c 'cd ~/IsaacLab && \
    ./isaaclab.sh \
    -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task=Isaac-Velocity-Rough-NoSensor-Spot-Micro-Play-v0 \
    --num_envs=50 \
    --checkpoint "/isaac-sim/IsaacLab/logs/rsl_rl/spot_micro_rough/2026-02-03_06-08-59/model_2000.pt"'