import os

path = "/isaac-sim/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/custom_quadruped/rough_env_cfg.py"

if not os.path.exists(path):
    print(f"File not found: {path}")
    exit(1)

with open(path, "r") as f:
    content = f.read()

# Add disabling lines to __post_init__
# We search for 'self.terminations.base_contact.params["sensor_cfg"].body_names = "trunk"' and add lines after it.

target_str = 'self.terminations.base_contact.params["sensor_cfg"].body_names = "trunk"'
replacement_str = 'self.terminations.base_contact.params["sensor_cfg"].body_names = "trunk"\n        # DISABLE SENSORS\n        self.scene.contact_forces = None\n        self.rewards.feet_air_time = None\n        self.terminations.base_contact = None'

if target_str in content:
    new_content = content.replace(target_str, replacement_str)
    with open(path, "w") as f:
        f.write(new_content)
    print("Patched rough_env_cfg.py")
else:
    print("Target string not found in rough_env_cfg.py")
    # Dump content for debugging if needed
    # print(content)
