"""
Configuration management for Aura.

This module provides Pydantic Settings-based configuration management
with support for YAML files, environment variables, and defaults.
"""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuraConfig(BaseSettings):
    """
    Aura configuration using Pydantic Settings.
    
    Automatically loads from:
    1. configs/config.yaml (or custom YAML file)
    2. Environment variables (with AURA_ prefix)
    3. Default values defined here
    """
    
    model_config = SettingsConfigDict(
        yaml_file='configs/config.yaml',
        yaml_file_encoding='utf-8',
        env_prefix='AURA_',
        env_nested_delimiter='__',
        case_sensitive=False,
    )
    
    # Docker settings
    optimizer_image: str = Field(
        default="registry-git.lsd.ufcg.edu.br/pedro.serey/awsome-savings:or-tools",
        description="Docker image for the optimizer container"
    )
    
    # Monitoring settings
    monitor_log_dir: str = Field(
        default="./monitor_logs",
        description="Directory where monitoring logs will be stored"
    )
    
    # Scheduler settings
    default_max_build: int = Field(
        default=2,
        description="Default maximum concurrent build jobs",
        ge=1
    )
    
    default_max_solve: int = Field(
        default=1,
        description="Default maximum concurrent solve jobs",
        ge=1
    )
    
    default_poll_interval: float = Field(
        default=0.2,
        description="Default polling interval in seconds",
        gt=0.0
    )
    
    # Storage settings
    runs_dir: str = Field(
        default="./orchestrator_runs",
        description="Directory for orchestrator run logs (JSONL files)"
    )
    
    max_old_runs: int = Field(
        default=100,
        description="Maximum number of old run logs to keep",
        ge=1
    )
    
    # Logging settings
    log_level: str = Field(
        default="INFO",
        description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    
    # Health and execution settings
    job_timeout: int = Field(
        default=3600,
        description="Maximum time to wait for a job to complete (seconds)",
        gt=0
    )
    
    # Docker execution settings
    families_mount: str = Field(
        default="/optimizer-files",
        description="Where to mount job family directories in container"
    )
    
    proto_mount: str = Field(
        default="/optimizer-proto",
        description="Where to mount proto files in container"
    )
    
    logs_mount: str = Field(
        default="/optimizer-logs",
        description="Where to mount logs in container"
    )
    
    # Debug settings
    verbose_docker: bool = Field(
        default=False,
        description="Enable verbose Docker output"
    )
    
    dry_run: bool = Field(
        default=False,
        description="Dry run mode (don't actually execute containers)"
    )


# Global configuration instance
_config: Optional[AuraConfig] = None


def get_config(config_file: Optional[Path] = None) -> AuraConfig:
    """
    Get global configuration instance.
    
    Args:
        config_file: Optional path to YAML config file
        
    Returns:
        AuraConfig instance
    """
    global _config
    
    if _config is None:
        if config_file:
            # Create config with custom file
            _config = AuraConfig(_env_file=None, _secrets_dir=None)
            _config.model_config = _config.model_config.copy()
            _config.model_config['yaml_file'] = str(config_file)
            # Reload with new config
            _config = AuraConfig(_env_file=None, _secrets_dir=None)
        else:
            _config = AuraConfig()
    
    return _config


def reload_config(config_file: Optional[Path] = None) -> AuraConfig:
    """
    Force reload global configuration.
    
    Args:
        config_file: Optional new path to config file
        
    Returns:
        AuraConfig instance with reloaded settings
    """
    global _config
    _config = None
    return get_config(config_file)


# Convenience functions to get specific config values
def get_optimizer_image() -> str:
    """Get Docker optimizer image name."""
    return get_config().optimizer_image


def get_monitor_log_dir() -> str:
    """Get monitoring log directory."""
    return get_config().monitor_log_dir


def get_runs_dir() -> str:
    """Get orchestrator runs directory."""
    return get_config().runs_dir
