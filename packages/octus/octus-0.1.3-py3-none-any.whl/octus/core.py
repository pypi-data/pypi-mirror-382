from pathlib import Path
import os
import logging
from typing import Type
from pydantic import BaseModel
from .loaders import load_yaml

logger = logging.getLogger(__name__)


class Octus:
    @classmethod
    def load(
        cls,
        base_path: str = ".",
        config_name: str = "config",
        env_var: str = "ENV_TYPE",
        config_model: Type[BaseModel] = BaseModel,
    ) -> BaseModel:
        base_path_obj = Path(base_path)

        config_file = base_path_obj / f"{config_name}.yaml"

        if env_value := os.getenv(env_var):
            env_config = base_path_obj / f"{config_name}.{env_value}.yaml"
            if env_config.exists():
                config_file = env_config
            else:
                raise FileNotFoundError(
                    f"Environment-specific config file not found: {env_config}"
                )

        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        config_data = load_yaml(config_file)
        logger.info(f"Configuration loaded from: {config_file}")

        return config_model(**config_data)
