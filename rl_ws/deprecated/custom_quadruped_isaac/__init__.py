import gymnasium as gym

from . import agent_cfg, env_cfg

##
# Register Gym environments.
##

gym.register(
    id="Isaac-Velocity-Rough-Custom-Quad-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": env_cfg.CustomQuadRoughEnvCfg,
        "rsl_rl_cfg_entry_point": agent_cfg.CustomQuadRoughPPORunnerCfg,
    },
)

gym.register(
    id="Isaac-Velocity-Rough-Custom-Quad-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": env_cfg.CustomQuadRoughEnvCfg_PLAY,
        "rsl_rl_cfg_entry_point": agent_cfg.CustomQuadRoughPPORunnerCfg,
    },
)

gym.register(
    id="Isaac-Velocity-Flat-Custom-Quad-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": env_cfg.CustomQuadFlatEnvCfg,
        "rsl_rl_cfg_entry_point": agent_cfg.CustomQuadFlatPPORunnerCfg,
    },
)

gym.register(
    id="Isaac-Velocity-Flat-Custom-Quad-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": env_cfg.CustomQuadFlatEnvCfg_PLAY,
        "rsl_rl_cfg_entry_point": agent_cfg.CustomQuadFlatPPORunnerCfg,
    },
)
