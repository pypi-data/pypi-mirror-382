#!/usr/bin/env python3
"""
Configuration Manager Lifecycle

OTP supervision for the configuration manager with self-scheduling reload.
Uses the new 0.5.0 OTPModule supervisor pattern.
"""

from otpylib import supervisor
from otpylib.supervisor import PERMANENT, ONE_FOR_ONE
from otpylib.module import OTPModule, SUPERVISOR

from otpylib_config.boundaries import ConfigManager
from otpylib_config.data import CONFIG_MANAGER, CONFIG_SUP, ConfigSpec


# =============================================================================
# Configuration Manager Supervisor
# =============================================================================

class ConfigSupervisor(metaclass=OTPModule, behavior=SUPERVISOR, version="1.0.0"):
    """
    Configuration Manager Supervisor.
    
    Manages the ConfigManager GenServer which self-schedules its own
    periodic reloads using process.send_after().
    """
    
    async def init(self, config_spec: ConfigSpec):
        """Initialize the config manager supervision tree."""
        genserver_spec = supervisor.child_spec(
            id=CONFIG_MANAGER,
            module=ConfigManager,
            args=config_spec,
            restart=PERMANENT,
            name=CONFIG_MANAGER,
        )
        
        children = [genserver_spec]
        
        opts = supervisor.options(
            strategy=ONE_FOR_ONE,
            max_restarts=3,
            max_seconds=60
        )
        
        return (children, opts)
    
    async def terminate(self, reason, state):
        """Cleanup on termination."""
        pass


# =============================================================================
# Lifecycle Functions
# =============================================================================

async def start(config_spec: ConfigSpec):
    """
    Start the Configuration Manager supervision tree.
    
    Returns the PID of the spawned supervisor.
    """
    return await supervisor.start_link(
        ConfigSupervisor,
        init_arg=config_spec,
        name=CONFIG_SUP
    )


async def stop():
    """Stop the Configuration Manager gracefully."""
    try:
        from otpylib import gen_server
        await gen_server.cast(CONFIG_MANAGER, "stop")
    except Exception:
        pass
