# Octus

A Python package designed to simplify configuration management for applications. It allows you to load configurations from YAML files, with support for environment-specific overrides and Pydantic for schema validation.

## Installation

```bash
pip install octus
```

## Usage

First, define your configuration schema using Pydantic:

```python
# my_app/config.py
from pydantic import BaseModel

class AppConfig(BaseModel):
    app_name: str
    version: str
    debug_mode: bool = False
```

Next, create your configuration file (e.g., `config.yaml`):

```yaml
# config.yaml
app_name: MyAwesomeApp
version: 1.0.0
debug_mode: true
```

You can also create environment-specific configuration files, like `config.development.yaml` or `config.production.yaml`. If the `APP_ENV` environment variable is set (e.g., `export APP_ENV=development`), `ConfigLoader` will attempt to load `config.{APP_ENV}.yaml` if it exists, overriding values from `config.yaml`.

Finally, use `Octopus` to load your configuration:

```python
# main.py
import os
from octus.core import Octus
from my_app.config import AppConfig

# Optional: Set environment variable for environment-specific config
# os.environ['ENV_TYPE'] = 'development' # Default env_var is ENV_TYPE

# Example 1: Basic usage with default env_var (ENV_TYPE)
config_loader = Octus.load(base_path=".", config_model=AppConfig)
print(f"App Name (default env): {config_loader.app_name}")

# Example 2: Specifying a different environment variable (e.g., APP_ENV)
os.environ['APP_ENV'] = 'production'
config_loader_env = Octus.load(base_path=".", env_var="APP_ENV", config_model=AppConfig)
print(f"App Name (APP_ENV): {config_loader_env.app_name}")

# Example 3: Loading without an environment variable (if no env_var is set)
os.environ.pop('ENV_TYPE', None) # Clear ENV_TYPE if set
os.environ.pop('APP_ENV', None) # Clear APP_ENV if set
config_loader_no_env = Octus.load(base_path=".", config_model=AppConfig)
print(f"App Name (no env): {config_loader_no_env.app_name}")

print(f"App Name: {config.app_name}")
print(f"Version: {config.version}")
print(f"Debug Mode: {config.debug_mode}")
```

## License

This project is licensed under the MIT License.