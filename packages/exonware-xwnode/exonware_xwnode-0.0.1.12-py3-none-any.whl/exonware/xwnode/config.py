"""
Configuration management for the xwnode library.

This module provides a thread-safe, centralized configuration for performance
tuning and behavior customization. It supports loading from environment
variables and programmatic overrides.
"""

import os
import threading
from dataclasses import dataclass, fields
from typing import Optional

# Assuming xSystem is in the path. If not, this will gracefully be handled.
try:
    from exonware.xwsystem import get_logger
    logger = get_logger('xwnode.config')
except (ImportError, TypeError):
    # Fallback logger if xwsystem is not available
    import logging
    logger = logging.getLogger('xwnode.config')

from .errors import XWNodeValueError

# A lock to ensure thread-safe modification of the global config object
_config_lock = threading.Lock()
# The global configuration instance
_config: Optional['XWNodeConfig'] = None


def _get_env_var(key: str, default: str, target_type: type):
    """
    Safely retrieve and cast an environment variable.

    Args:
        key: The environment variable name.
        default: The default value (as a string).
        target_type: The type to cast the value to (int, float, bool).

    Returns:
        The casted value.

    Raises:
        xNodeValueError: If the environment variable has an invalid value.
    """
    value = os.getenv(key, default)
    try:
        if target_type is bool:
            return value.lower() in ('true', '1', 'yes', 'y', 't')
        if target_type is int:
            return int(value)
        if target_type is float:
            return float(value)
        return value
    except (ValueError, TypeError) as e:
        raise xNodeValueError(
            f"Invalid value for environment variable {key}: '{value}'. "
            f"Could not convert to {target_type.__name__}."
        ) from e


@dataclass
class XWNodeConfig:
    """
    Configuration for XWNode performance and behavior tuning.

    Defines default values for various operational parameters. These can be
    overridden by environment variables or by setting a custom config object.
    """

    # --- Cache Configuration ---
    path_cache_size: int = 1024
    node_pool_size: int = 2000
    conversion_cache_size: int = 512

    # --- Lazy Loading Thresholds ---
    lazy_threshold_dict: int = 15
    lazy_threshold_list: int = 30

    # --- Memory Management ---
    enable_weak_refs: bool = True
    enable_object_pooling: bool = True

    # --- Security Limits ---
    max_depth: int = 100
    max_nodes: int = 1_000_000
    max_path_length: int = 1024

    # --- Performance Features ---
    enable_path_caching: bool = True
    enable_conversion_caching: bool = True
    enable_optimized_iteration: bool = True

    # --- Threading ---
    enable_thread_safety: bool = True
    lock_timeout: float = 5.0

    @classmethod
    def from_env(cls) -> 'XWNodeConfig':
        """
        Load configuration from environment variables, with robust type casting.
        """
        logger.debug("Loading XWNode configuration from environment variables.")
        kwargs = {}
        for field in fields(cls):
            env_key = f"XNODE_{field.name.upper()}"
            kwargs[field.name] = _get_env_var(env_key, str(field.default), field.type)
        return cls(**kwargs)

    def validate(self) -> None:
        """
        Validate configuration values, raising specific errors on failure.

        Raises:
            XWNodeValueError: If any configuration value is invalid.
        """
        if self.path_cache_size <= 0:
            raise XWNodeValueError("path_cache_size must be positive")
        if self.node_pool_size <= 0:
            raise XWNodeValueError("node_pool_size must be positive")
        if self.lazy_threshold_dict < 0:
            raise XWNodeValueError("lazy_threshold_dict must be non-negative")
        if self.lazy_threshold_list < 0:
            raise XWNodeValueError("lazy_threshold_list must be non-negative")
        if self.max_depth <= 0:
            raise XWNodeValueError("max_depth must be positive")
        if self.max_nodes <= 0:
            raise XWNodeValueError("max_nodes must be positive")
        if self.max_path_length <= 0:
            raise XWNodeValueError("max_path_length must be positive")
        if self.lock_timeout <= 0:
            raise XWNodeValueError("lock_timeout must be positive")


def get_config() -> XWNodeConfig:
    """
    Get the global, thread-safe XWNode configuration instance.

    Initializes the configuration from environment variables on first call.
    """
    global _config
    # Fast path to avoid locking if config is already set
    if _config is not None:
        return _config

    # Thread-safe initialization
    with _config_lock:
        # Check again in case another thread initialized it while we waited for the lock
        if _config is None:
            _config = XWNodeConfig.from_env()
            _config.validate()
            logger.info(f"Initialized XWNode configuration: {_config}")
    return _config


def set_config(config: XWNodeConfig) -> None:
    """
    Set the global XWNode configuration. This is a thread-safe operation.

    Args:
        config: A validated XWNodeConfig instance.
    """
    global _config
    config.validate()
    with _config_lock:
        _config = config
        logger.info(f"Updated XWNode configuration: {config}")


def reset_config() -> None:
    """
    Reset the global configuration to its default state (loaded from env).
    This is a thread-safe operation.
    """
    global _config
    with _config_lock:
        _config = None
        logger.info("Reset XWNode configuration. It will be re-initialized on next get_config() call.")
