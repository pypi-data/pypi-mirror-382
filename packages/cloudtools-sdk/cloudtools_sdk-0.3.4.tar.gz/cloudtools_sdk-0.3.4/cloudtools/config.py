"""Configuration utilities for CloudTools SDK."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, Optional

LOGGER = logging.getLogger(__name__)

_tunnel_env_cache: Optional[Dict[str, str]] = None


def load_tunnel_env() -> Dict[str, str]:
    """Load environment variables from .env.tunnel file if it exists."""
    global _tunnel_env_cache
    
    if _tunnel_env_cache is not None:
        return _tunnel_env_cache
    
    try:
        project_root = Path(__file__).resolve().parents[2]
        env_file = project_root / ".env.tunnel"
        if env_file.exists():
            env_vars = {}
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
            _tunnel_env_cache = env_vars
            return env_vars
    except Exception as e:
        LOGGER.debug(f"Could not load .env.tunnel: {e}")
    
    _tunnel_env_cache = {}
    return _tunnel_env_cache


def get_config_value(*keys: str, default: str, explicit: Optional[str] = None, strip_slash: bool = False) -> str:
    """Get configuration value with precedence: explicit > env vars > tunnel file > default.
    
    Args:
        *keys: Environment variable keys to check in order
        default: Default value if none found
        explicit: Explicit value that takes precedence over everything
        strip_slash: Whether to strip trailing slashes from the result
    
    Returns:
        The first matching value or default
    """
    if explicit:
        return explicit.rstrip("/") if strip_slash else explicit
    
    for key in keys:
        value = os.getenv(key)
        if value:
            return value.rstrip("/") if strip_slash else value
    
    tunnel_env = load_tunnel_env()
    for key in keys:
        value = tunnel_env.get(key)
        if value:
            return value.rstrip("/") if strip_slash else value
    
    return default.rstrip("/") if strip_slash else default

