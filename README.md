# pydanticutils
[![ci status](https://github.com/rupurt/pydanticutils/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/rupurt/pydanticutils/actions/workflows/ci.yaml)
![pypi](https://img.shields.io/pypi/v/pydanticutils.svg)
![versions](https://img.shields.io/pypi/pyversions/pydanticutils.svg)

Pydantic utility helpers

## Usage

1. Install the package from pypi

```console
> pip install pydanticutils
```

2. Create a pydantic settings class

```python
class DatabaseSettings(BaseModel):
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=5432)


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_nested_delimiter="__")

    log_level: str = Field(default="INFO")
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
```

3. Read a configuration file into the settings class

```python
from pydanticutils import read_yaml

settings = read_yaml("/path/to/config.yaml", AppSettings)
```

## Development

This repository manages the dev environment as a Nix flake and requires [Nix to be installed](https://github.com/DeterminateSystems/nix-installer)

```console
> nix develop -c $SHELL
```

```shell
> make setup
```

```shell
> make test
```

## Publish Package to PyPi

```shell
> make distribution
```

## License

`pydanticutils` is released under the [MIT license](./LICENSE)
