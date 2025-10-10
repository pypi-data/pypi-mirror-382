import pytest
from pydantic import BaseModel, ValidationError

from octus.core import Octus
from octus.loaders import load_yaml


class AppSettings(BaseModel):
    name: str
    version: str
    debug: bool = False


class DatabaseSettings(BaseModel):
    host: str
    port: int


class Config(BaseModel):
    app: AppSettings
    database: DatabaseSettings


@pytest.fixture
def temp_config_dir(tmp_path):
    """Creates a temporary directory with config files for testing."""
    (tmp_path / "config.yaml").write_text("""
app:
  name: TestApp
  version: 1.0.0
database:
  host: localhost
  port: 5432
""")
    (tmp_path / "config.development.yaml").write_text("""
app:
  name: TestAppDev
  version: 1.0.1
  debug: true
database:
  host: dev.localhost
  port: 5433
""")
    (tmp_path / "my_custom_config.yaml").write_text("""
app:
  name: CustomApp
  version: 2.0.0
database:
  host: custom.localhost
  port: 8000
""")
    (tmp_path / "my_custom_config.production.yaml").write_text("""
app:
  name: WeAreInProduction
  version: 2.0.0
database:
  host: production.host
  port: 80
""")
    return tmp_path


def test_load_yaml(temp_config_dir):
    """Test that load_yaml correctly loads a YAML file."""
    config_data = load_yaml(temp_config_dir / "config.yaml")
    assert config_data["app"]["name"] == "TestApp"
    assert config_data["database"]["port"] == 5432


def test_config_loader_load_default(temp_config_dir, monkeypatch):
    """Test ConfigLoader loads the default config.yaml."""
    monkeypatch.delenv("ENV_TYPE", raising=False)
    config = Octus.load(base_path=str(temp_config_dir), config_model=Config)
    assert config.app.name == "TestApp"
    assert config.app.version == "1.0.0"
    assert config.database.host == "localhost"
    assert config.database.port == 5432
    assert config.app.debug is False  # Default value


def test_config_loader_load_environment_specific(temp_config_dir, monkeypatch):
    """Test ConfigLoader loads environment-specific config."""
    monkeypatch.setenv("ENV_TYPE", "development")
    config = Octus.load(base_path=str(temp_config_dir), config_model=Config)
    assert config.app.name == "TestAppDev"
    assert config.app.version == "1.0.1"
    assert config.app.debug
    assert config.database.host == "dev.localhost"
    assert config.database.port == 5433


def test_config_loader_error_loading_without_related_type(temp_config_dir, monkeypatch):
    """Test ConfigLoader raises an error if ENV_TYPE is set, but we do not have an environment-specific config."""
    monkeypatch.setenv("ENV_TYPE", "dev")
    with pytest.raises(FileNotFoundError):
        Octus.load(base_path=str(temp_config_dir), config_model=Config)


def test_config_loader_file_not_found(temp_config_dir):
    """Test ConfigLoader raises FileNotFoundError if config file is missing."""
    with pytest.raises(FileNotFoundError):
        Octus.load(
            base_path=str(temp_config_dir / "non_existent_dir"), config_model=Config
        )


def test_config_loader_custom_env_var(temp_config_dir, monkeypatch):
    """Test ConfigLoader uses a custom environment variable."""
    monkeypatch.setenv("MY_ENV_TYPE", "development")
    config = Octus.load(
        base_path=str(temp_config_dir), env_var="MY_ENV_TYPE", config_model=Config
    )
    assert config.app.name == "TestAppDev"
    assert config.app.version == "1.0.1"
    assert config.app.debug
    assert config.database.host == "dev.localhost"
    assert config.database.port == 5433


def test_config_loader_validation_error(tmp_path, monkeypatch):
    """Test ConfigLoader raises ValidationError for invalid config."""
    monkeypatch.delenv("ENV_TYPE", raising=False)
    (tmp_path / "config.yaml").write_text("""
app:
  name: TestApp
  version: 1.0.0
database:
  host: localhost
  port: "not_an_int" # Invalid type
""")

    with pytest.raises(ValidationError):
        Octus.load(base_path=str(tmp_path), config_model=Config)


def test_config_loader_custom_config_name(temp_config_dir, monkeypatch):
    """Test ConfigLoader loads a config file with a custom name."""
    monkeypatch.delenv("ENV_TYPE", raising=False)
    config = Octus.load(
        base_path=str(temp_config_dir),
        config_name="my_custom_config",
        config_model=Config,
    )
    assert config.app.name == "CustomApp"
    assert config.app.version == "2.0.0"
    assert config.database.host == "custom.localhost"
    assert config.database.port == 8000


def test_config_loader_custom_config_name_for_dev(temp_config_dir, monkeypatch):
    """Test ConfigLoader loads a config file with a custom name with env type."""
    monkeypatch.setenv("ENV_TYPE", "production")
    config = Octus.load(
        base_path=str(temp_config_dir),
        config_name="my_custom_config",
        config_model=Config,
    )
    assert config.app.name == "WeAreInProduction"
    assert config.app.version == "2.0.0"
    assert config.database.host == "production.host"
    assert config.database.port == 80
