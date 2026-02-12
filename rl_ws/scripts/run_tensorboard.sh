#!/bin/bash
docker exec -it isaac-sim bash -c "cd ~/IsaacLab && ./isaaclab.sh -p -m tensorboard.main --logdir logs/rsl_rl --port 6006 --bind_all"
