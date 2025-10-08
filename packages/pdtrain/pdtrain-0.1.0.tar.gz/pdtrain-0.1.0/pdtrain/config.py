"""Configuration management for pdtrain CLI"""

import os
import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class Config(BaseModel):
    """Configuration for pdtrain CLI"""

    api_url: str = Field(default="http://localhost:8000", description="API base URL")
    api_key: Optional[str] = Field(default=None, description="API authentication key")

    @classmethod
    def get_config_path(cls) -> Path:
        """Get path to config file"""
        config_dir = Path.home() / ".pdtrain"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "config.json"

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file or environment"""
        config_path = cls.get_config_path()

        # Start with defaults
        config_data = {}

        # Load from file if exists
        if config_path.exists():
            with open(config_path, "r") as f:
                config_data = json.load(f)

        # Override with environment variables
        if os.getenv("PDTRAIN_API_URL"):
            config_data["api_url"] = os.getenv("PDTRAIN_API_URL")

        if os.getenv("PDTRAIN_API_KEY"):
            config_data["api_key"] = os.getenv("PDTRAIN_API_KEY")

        return cls(**config_data)

    def save(self) -> None:
        """Save configuration to file"""
        config_path = self.get_config_path()
        with open(config_path, "w") as f:
            json.dump(self.model_dump(exclude_none=True), f, indent=2)

    def is_configured(self) -> bool:
        """Check if CLI is properly configured"""
        return self.api_key is not None and self.api_url is not None


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance"""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def set_config(config: Config) -> None:
    """Set global config instance"""
    global _config
    _config = config
