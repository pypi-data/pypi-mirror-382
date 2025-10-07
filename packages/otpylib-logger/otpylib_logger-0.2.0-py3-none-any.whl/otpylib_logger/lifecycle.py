#!/usr/bin/env python3
"""
Logger Lifecycle Management

Supervisor that manages the LoggerManager GenServer and Handler processes.
"""

import asyncio
import importlib

from otpylib import supervisor, process
from otpylib.supervisor import PERMANENT, ONE_FOR_ONE
from otpylib.module import OTPModule, SUPERVISOR

from otpylib_logger.atoms import LOGGER, LOGGER_SUP
from otpylib_logger.data import LoggerSpec
from otpylib_logger.boundaries import LoggerManager


# =============================================================================
# Logger Supervisor Module
# =============================================================================

class LoggerSupervisor(metaclass=OTPModule, behavior=SUPERVISOR, version="1.0.0"):
    """
    Logger Supervisor.
    
    Manages LoggerManager GenServer and all handler processes.
    """
    
    async def init(self, logger_spec: LoggerSpec):
        """Initialize the logger supervision tree."""
        # Import handler modules dynamically
        handlers = []
        for handler_spec in logger_spec.handlers:
            handler_module = importlib.import_module(handler_spec.handler_module)
            handler_start_func = getattr(handler_module, "start_link")
            handlers.append((handler_spec, handler_start_func))
        
        # Build supervision tree
        children = [
            supervisor.child_spec(
                id="logger_manager",
                module=LoggerManager,
                args=logger_spec,
                restart=PERMANENT,
                name=LOGGER
            ),
        ]
        
        # Add handlers as supervised children
        for handler_spec, start_func in handlers:
            # Merge handler level into config
            handler_config = {
                **handler_spec.config,
                "level": handler_spec.level,
            }
            
            children.append(
                supervisor.child_spec(
                    id=f"handler_{handler_spec.name}",
                    func=start_func,
                    args=[handler_config],
                    restart=PERMANENT,
                )
            )
        
        opts = supervisor.options(strategy=ONE_FOR_ONE)
        
        return (children, opts)
    
    async def terminate(self, reason, state):
        """Cleanup on termination."""
        pass


# =============================================================================
# Lifecycle Functions
# =============================================================================

async def start_link(logger_spec: LoggerSpec):
    """
    Start the logger supervision tree.
    Returns the PID of the spawned supervisor.
    """
    return await supervisor.start_link(
        LoggerSupervisor,
        init_arg=logger_spec,
        name=LOGGER_SUP
    )
