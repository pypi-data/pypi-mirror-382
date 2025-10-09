from pydantic import BaseModel, ConfigDict
from typing import TypeVar, Generic, Type, Any
from pathlib import Path
import json


class ConfigBase(BaseModel):
    """Base class for configuration models.
    
    All configuration models should inherit from this class.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
T = TypeVar('T', bound=ConfigBase)

class ConfigHolder(Generic[T]):
    _config: T | None = None
    _data_model: Type[T]
    _config_path: Path

    def __init__(self, data_model: Type[T], config_path: str | Path, default_config: T | None = None):
        self._config = default_config
        self._data_model = data_model
        self._config_path = Path(config_path)

        if not self._config_path.is_file():
            if self._config is None:
                raise FileNotFoundError(f"Configuration file '{self._config_path}' does not exist and no default config provided.")
            else:
                self.save()
        else:
            self.load()

    @property
    def config(self) -> T | None:
        return self._config

    @property
    def info(self) -> dict[str, Any]:
        if self._config is None:
            raise ValueError("Configuration has not been loaded.")
        return {
            "config_path": str(self._config_path),
            "config_type": self._data_model.__name__,
            "config_data": self._config.model_dump()
        }

    def validate_config(self, config_data: dict[str, Any] | str) -> None:
        if isinstance(config_data, str):
            data_dict = json.loads(config_data)
        else:
            data_dict = config_data
        self._config = self._data_model(**data_dict)

    def load(self) -> None:
        with open(self._config_path, 'r') as f:
            self.validate_config(json.load(f))

    def save(self) -> None:
        if self._config is None:
            raise ValueError("No configuration to save.")
        with open(self._config_path, 'w') as f:
            json.dump(self._config.model_dump(), f, indent=4)

# Global variable to store the current config holder (for backward compatibility)
_global_config_holder: ConfigHolder[Any] | None = None

def get_config() -> Any:
    """Get the current configuration instance. Returns the actual config type set via set_config."""
    if _global_config_holder is None:
        raise ValueError("Configuration has not been initialized. Call set_config() first.")
    if _global_config_holder.config is None:
        raise ValueError("Configuration has not been loaded. Call load_config() first.")
    return _global_config_holder.config

def set_config(config_model: Type[T], config_path: str, default_config: T | None = None) -> T:
    """Set the configuration model class to use."""
    global _global_config_holder
    if _global_config_holder is None:
        _global_config_holder = ConfigHolder(data_model=config_model, config_path=config_path, default_config=default_config)
    if _global_config_holder.config is None:
        raise ValueError("Configuration has not been loaded. Call load_config() first.")
    return _global_config_holder.config

def reset_config() -> None:
    """Reset the current configuration."""
    global _global_config_holder
    if _global_config_holder is not None:
        _global_config_holder = None

def get_config_info() -> dict[str, Any]:
    """Get information about the current configuration."""
    if _global_config_holder is None or _global_config_holder.config is None:
        raise ValueError("Configuration has not been initialized or loaded.")
    return _global_config_holder.info
