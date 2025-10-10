import json
from pathlib import Path
import yaml

from .exceptions import ConfigError


class ConfigLoader:
    """
        Basic configuration loader for config files. Currently, supports JSON and YAML formats.
        It returns a dictionary representation of the config file.
    """

    @staticmethod
    def load(file_path: str, schema: dict = None) -> dict:
        path = Path(file_path)

        if not path.exists():
            raise ConfigError(f"Config file not found: {file_path}")

        if path.suffix.lower() == ".json":
            with open(path, "r", encoding="utf-8") as f:
                file_content = json.load(f)
        elif path.suffix.lower() in ['.yaml', '.yml']:
            with open(path, "r", encoding="utf-8") as f:
                file_content = yaml.safe_load(f)
        else:
            raise ConfigError(f"Unsupported config format: {path.suffix}")

        if schema:
            ConfigLoader.validate_schema(file_content, schema)

        return file_content

    @staticmethod
    def validate_schema(config: dict, schema: dict) -> bool:
        """
            Validate a config file dictionary representation against a defined schema.
            Returns true if its valid or raises ConfigError.
        """

        for key, value_type in schema.items():
            if key not in config:
                raise ConfigError(f"Missing required key: {key}")

            if isinstance(value_type, dict):
                if not isinstance(config[key], dict):
                    raise ConfigError(f"Key {key} should be a dict")

                ConfigLoader.validate_schema(config[key], value_type)
            else:
                if not isinstance(config[key], value_type):
                    raise ConfigError(f"Incorrect type for key: {key}. Expected {value_type}, got {type(config[key])}")
        return True
