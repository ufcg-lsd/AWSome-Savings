"""
Configuration management for Aura.

This module provides Pydantic Settings-based configuration management
with support for YAML files, environment variables, and defaults.
"""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource
from pydantic_settings.sources import PydanticBaseSettingsSource


class DockerConfig(BaseModel):
    """Docker-related configuration."""
    optimizer_image: str = Field(
        default="registry-git.lsd.ufcg.edu.br/pedro.serey/awsome-savings:or-tools",
        description="Docker image for the optimizer container"
    )
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
    verbose_docker: bool = Field(
        default=False,
        description="Enable verbose Docker output"
    )
    dry_run: bool = Field(
        default=False,
        description="Dry run mode (don't actually execute containers)"
    )


class SchedulerConfig(BaseModel):
    """Scheduler-related configuration."""
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
    job_timeout: int = Field(
        default=3600,
        description="Maximum time to wait for a job to complete (seconds)",
        gt=0
    )


class StorageConfig(BaseModel):
    """Storage-related configuration."""
    runs_dir: str = Field(
        default="./orchestrator_runs",
        description="Directory for orchestrator run logs (JSONL files)"
    )
    max_old_runs: int = Field(
        default=100,
        description="Maximum number of old run logs to keep",
        ge=1
    )


class MonitoringConfig(BaseModel):
    """Monitoring-related configuration."""
    log_dir: str = Field(
        default="./monitor_logs",
        description="Directory where monitoring logs will be stored"
    )


class LoggingConfig(BaseModel):
    """Logging-related configuration."""
    level: str = Field(
        default="INFO",
        description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )


class AuraConfig(BaseSettings):
    """
    Aura configuration using Pydantic Settings with nested sections.
    
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
    
    docker: DockerConfig = Field(default_factory=DockerConfig)
    scheduler: SchedulerConfig = Field(default_factory=SchedulerConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Customize settings sources to include YAML file loading.
        
        Order of precedence (highest to lowest):
        1. init_settings (arguments passed to constructor)
        2. env_settings (environment variables)
        3. yaml_settings (YAML file)
        4. dotenv_settings (.env file)
        5. file_secret_settings (Docker secrets)
        """
        yaml_settings = YamlConfigSettingsSource(
            settings_cls,
            yaml_file=settings_cls.model_config.get('yaml_file'),
            yaml_file_encoding=settings_cls.model_config.get('yaml_file_encoding', 'utf-8'),
        )
        return (
            init_settings,
            env_settings, 
            yaml_settings,
            dotenv_settings,
            file_secret_settings,
        )
    
    # Convenience properties for backward compatibility
    @property
    def optimizer_image(self) -> str:
        return self.docker.optimizer_image
    
    @property
    def default_max_build(self) -> int:
        return self.scheduler.default_max_build
    
    @property
    def default_max_solve(self) -> int:
        return self.scheduler.default_max_solve
    
    @property
    def default_poll_interval(self) -> float:
        return self.scheduler.default_poll_interval
    
    @property
    def runs_dir(self) -> str:
        return self.storage.runs_dir
    
    @property
    def monitor_log_dir(self) -> str:
        return self.monitoring.log_dir
    
    @property
    def families_mount(self) -> str:
        return self.docker.families_mount
    
    @property
    def proto_mount(self) -> str:
        return self.docker.proto_mount
    
    @property
    def logs_mount(self) -> str:
        return self.docker.logs_mount
    
    @property
    def log_level(self) -> str:
        return self.logging.level
    
    @property
    def log_format(self) -> str:
        return self.logging.format
    
    @property
    def job_timeout(self) -> int:
        return self.scheduler.job_timeout
    
    @property
    def verbose_docker(self) -> bool:
        return self.docker.verbose_docker
    
    @property
    def dry_run(self) -> bool:
        return self.docker.dry_run
    
    @property
    def max_old_runs(self) -> int:
        return self.storage.max_old_runs


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
