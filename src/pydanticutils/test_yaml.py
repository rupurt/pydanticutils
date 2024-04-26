import os
from pathlib import Path
from textwrap import dedent
from typing import Tuple, Type
from unittest import mock

import pydantic
import pytest
from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from pydanticutils import YAMLScannerError, read_yaml


def test_read_yaml_defaults(config_path_not_found):
    settings = read_yaml(config_path_not_found, FileOverrideEnvSettings)
    assert settings.log_level == "INFO"
    assert settings.database.host == "0.0.0.0"
    assert settings.database.port == 5432


def test_read_yaml_file(config_path):
    settings = read_yaml(config_path, FileOverrideEnvSettings)
    assert settings.log_level == "DEBUG"
    assert settings.database.host == "1.1.1.1"
    assert settings.database.port == 5432


@mock.patch.dict(
    os.environ,
    {"MYAPP_LOG_LEVEL": "WARN", "MYAPP_DATABASE__HOST": "2.2.2.2"},
    clear=True,
)
def test_read_yaml_file_override_env_vars(config_path):
    settings = read_yaml(config_path, FileOverrideEnvSettings)
    assert settings.log_level == "DEBUG"
    assert settings.database.host == "1.1.1.1"
    assert settings.database.port == 5432


@mock.patch.dict(
    os.environ,
    {"MYAPP_LOG_LEVEL": "WARN", "MYAPP_DATABASE__PORT": "5433"},
    clear=True,
)
def test_read_yaml_env_vars_override_file(config_path):
    settings = read_yaml(config_path, EnvOverrideFileSettings)
    assert settings.log_level == "WARN"
    assert settings.database.host == "1.1.1.1"
    assert settings.database.port == 5433


def test_read_yaml_error_invalid_file(config_path_invalid_yaml):
    with pytest.raises(YAMLScannerError, match=r"while scanning a simple key.*"):
        read_yaml(config_path_invalid_yaml, FileOverrideEnvSettings)


@mock.patch.dict(
    os.environ,
    {"MYAPP_DATABASE__PORT": "abc"},
    clear=True,
)
def test_read_yaml_error_invalid_env_var(config_path):
    with pytest.raises(
        pydantic.ValidationError, match=r"validation error for EnvOverrideFileSettings"
    ):
        read_yaml(config_path, EnvOverrideFileSettings)


@pytest.fixture()
def config_path_not_found(tmpdir):
    return tmpdir / "notfound.yaml"


@pytest.fixture()
def config_path(tmpdir):
    config_path = Path(tmpdir) / "config.yaml"
    config_path.write_text(
        dedent("""\
        log_level: DEBUG
        database:
            host: 1.1.1.1
        """)
    )
    return config_path


@pytest.fixture()
def config_path_invalid_yaml(tmpdir):
    config_path = Path(tmpdir) / "config_invalid.yaml"
    config_path.write_text(
        dedent("""\
        log_level: DEBUG
        database
        """)
    )
    return config_path


class DatabaseSettings(BaseModel):
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=5432)


class FileOverrideEnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MYAPP_", env_nested_delimiter="__")

    log_level: str = Field(default="INFO")
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)


class EnvOverrideFileSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MYAPP_", env_nested_delimiter="__")

    log_level: str = Field(default="INFO")
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return env_settings, dotenv_settings, file_secret_settings, init_settings
