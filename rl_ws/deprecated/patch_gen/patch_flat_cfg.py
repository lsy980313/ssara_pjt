import os

path = "/isaac-sim/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/custom_quadruped/flat_env_cfg.py"

if not os.path.exists(path):
    print(f"File not found: {path}")
    exit(1)

with open(path, "r") as f:
    content = f.read()

# Comment out self.rewards.feet_air_time.weight
target_str = 'self.rewards.feet_air_time.weight = 0.25'
replacement_str = '# self.rewards.feet_air_time.weight = 0.25'

if target_str in content:
    new_content = content.replace(target_str, replacement_str)
    with open(path, "w") as f:
        f.write(new_content)
    print("Patched flat_env_cfg.py")
else:
    print("Target string not found in flat_env_cfg.py")
