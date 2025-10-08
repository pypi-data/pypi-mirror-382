#!/usr/bin/env python3
"""
Configuration Manager GenServer

The core GenServer that manages configuration state, sources, and subscriptions.
Uses atom-based message dispatch for high performance.
Self-schedules periodic reloads using process.send_after().
"""

from typing import Any
from otpylib import atom, process
from otpylib.module import OTPModule, GEN_SERVER
from otpylib.gen_server.data import Reply, NoReply, Stop

from result import Result

from otpylib_config.atoms import (
    GET_CONFIG, PUT_CONFIG, SUBSCRIBE, UNSUBSCRIBE, RELOAD,
    PING, STOP as STOP_ATOM, STATUS, RELOAD_TICK,
    time_atom_comparison,
)
from otpylib_config.data import ConfigManagerState, CONFIG_MANAGER, ConfigSpec
from otpylib_config import core


OK = atom.ensure("ok")


# =============================================================================
# Configuration Manager GenServer Module
# =============================================================================

class ConfigManager(metaclass=OTPModule, behavior=GEN_SERVER, version="1.0.0"):
    """
    Configuration Manager GenServer.
    
    Manages configuration state, sources, and subscriptions with
    atom-based message dispatch for high performance.
    
    Self-schedules periodic reloads using process.send_after().
    """
    
    async def init(self, config_spec: ConfigSpec):
        """Initialize configuration manager with sources."""
        print("[TRACE:config_mgr.init] ENTER")

        state = ConfigManagerState(
            sources=config_spec.sources if hasattr(config_spec, "sources") else [],
            reload_interval=getattr(config_spec, "reload_interval", 30.0),
        )

        # Load initial configuration from all sources
        result: Result = await core.reconcile_configuration(state)
        if result.is_err():
            err = result.unwrap_err()
            print(f"[TRACE:config_mgr.init] reconcile_configuration failed: {err}")
            raise Exception(err)  # let supervisor treat this as init crash
        else:
            print("[TRACE:config_mgr.init] reconcile_configuration succeeded")
            
            # Schedule first reload tick to ourselves
            my_pid = process.self()
            await process.send_after(state.reload_interval, my_pid, RELOAD_TICK)
            print(f"[TRACE:config_mgr.init] Scheduled first reload in {state.reload_interval}s")
            
            return state
    
    async def handle_call(self, message, from_, state: ConfigManagerState):
        """Handle synchronous configuration requests using atom dispatch."""
        match message:
            case msg_type, path_str, default if time_atom_comparison(msg_type, GET_CONFIG):
                result = await core.get_config_value(path_str, default, state)
                if result.is_ok():
                    return (Reply(payload=result.unwrap()), state)
                else:
                    return (Reply(payload=Exception(result.unwrap_err())), state)

            case msg_type, path_str, value if time_atom_comparison(msg_type, PUT_CONFIG):
                result = await core.ensure_config_value(path_str, value, state)
                if result.is_ok():
                    change_info = result.unwrap()
                    if change_info["changed"]:
                        await _notify_subscribers(
                            state,
                            change_info["path"],
                            change_info["old_value"],
                            change_info["new_value"],
                        )
                    return (Reply(payload=True), state)
                else:
                    return (Reply(payload=Exception(result.unwrap_err())), state)

            case msg_type, pattern_str, callback, subscriber_pid if time_atom_comparison(msg_type, SUBSCRIBE):
                result = await core.ensure_subscription(pattern_str, callback, subscriber_pid, state)
                return (
                    Reply(payload=True if result.is_ok() else Exception(result.unwrap_err())),
                    state,
                )

            case msg_type, pattern_str, callback, subscriber_pid if time_atom_comparison(msg_type, UNSUBSCRIBE):
                result = await core.ensure_subscription_absent(pattern_str, callback, subscriber_pid, state)
                return (
                    Reply(payload=True if result.is_ok() else Exception(result.unwrap_err())),
                    state,
                )

            case msg_type if time_atom_comparison(msg_type, PING):
                return (Reply(payload="pong"), state)

            case msg_type if time_atom_comparison(msg_type, STATUS):
                result = await core.get_manager_status(state)
                return (
                    Reply(payload=result.unwrap() if result.is_ok() else Exception(result.unwrap_err())),
                    state,
                )

            case _:
                return (Reply(payload=NotImplementedError(f"Unknown call: {message}")), state)
    
    async def handle_cast(self, message, state: ConfigManagerState):
        """Handle asynchronous configuration updates."""
        match message:
            case msg_type if time_atom_comparison(msg_type, RELOAD):
                result = await core.reconcile_configuration(state)
                if result.is_ok():
                    await _notify_reload_changes(state, result)
                return (NoReply(), state)

            case msg_type if time_atom_comparison(msg_type, STOP_ATOM):
                return (Stop(reason=None), state)

            case ("source_update", source_name, new_config):
                result = await core.reconcile_configuration(state)
                if result.is_ok():
                    await _notify_reload_changes(state, result)
                return (NoReply(), state)

            case _:
                return (NoReply(), state)
    
    async def handle_info(self, message, state: ConfigManagerState):
        """Handle info messages (reload ticks and direct mailbox sends)."""
        match message:
            case msg_type if time_atom_comparison(msg_type, RELOAD_TICK):
                # Perform reload
                old_config = state.config.copy()
                result = await core.reconcile_configuration(state)
                if result.is_ok():
                    reload_result = result.unwrap()
                    if reload_result.config_changes > 0:
                        await _notify_config_changes(state, old_config, state.config)
                
                # Schedule next reload tick (self-scheduling pattern)
                my_pid = process.self()
                await process.send_after(state.reload_interval, my_pid, RELOAD_TICK)
                
                return (NoReply(), state)

            case _:
                return (NoReply(), state)
    
    async def terminate(self, reason, state: ConfigManagerState):
        """Cleanup on termination."""
        pass


# =============================================================================
# Internal Helper Functions
# =============================================================================

async def _notify_subscribers(state, path: str, old_value: Any, new_value: Any):
    """Notify pattern-matched subscribers of a configuration change."""
    matching_subscriptions = core.get_matching_subscribers(path, state)

    for subscriber_pid, callback in matching_subscriptions:
        try:
            await callback(subscriber_pid, path, old_value, new_value)
        except Exception:
            pass


async def _notify_reload_changes(state, reload_result):
    """Notify subscribers of configuration changes detected during reload."""
    pass


async def _notify_config_changes(state, old_config: dict, new_config: dict):
    """Notify subscribers of specific configuration changes."""
    changes = core.get_config_differences(old_config, new_config)

    for change in changes:
        await _notify_subscribers(
            state, change["path"], change["old_value"], change["new_value"]
        )
