from os import PathLike
from typing import Type, TypeVar

import yaml
import yaml.scanner
from pydantic_settings import BaseSettings

T = TypeVar("T", bound=BaseSettings)


def read_yaml(path: PathLike, cls: Type[T]) -> T:
    """
    Read a yaml file that `may` or `may not` exist and return a pydantic
    base settings instance hydrated with a combination of defaults,
    file contents and environment variables.

    The pydantic default order of precedence is:
        1. yaml file
        2. environment variables
        3. python defined default values

    The precedence order can be controlled by overriding the
    `settings_customise_source` method of the `BaseSettings` class.

    ```
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
    ```
    """
    yaml_config = {}
    try:
        with open(path, "r") as fd:
            yaml_config = yaml.safe_load(fd) or {}
    except FileNotFoundError:
        pass
    except yaml.scanner.ScannerError as e:
        raise YAMLScannerError(e)
    return cls(**yaml_config)


class YAMLScannerError(yaml.scanner.ScannerError):
    def __init__(self, err: yaml.scanner.ScannerError):
        super().__init__(
            context=err.context,
            context_mark=err.context_mark,
            problem=err.problem,
            problem_mark=err.problem_mark,
            note=err.note,
        )
