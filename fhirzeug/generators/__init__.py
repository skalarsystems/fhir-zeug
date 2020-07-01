import yaml
from pathlib import Path
from typing import Optional
from .yaml_model import GeneratorConfig

GENERATOR_FILENAME = "generator.yaml"


class ConfigNotFoundException(Exception):
    pass


def load_config(config_name: Optional[str] = None) -> GeneratorConfig:
    """ Load config for a specific generator.
    Missing values are replaced by default values from `default/` folder.
    """
    dir_path = Path(__file__).parent
    default_path = dir_path / "default" / GENERATOR_FILENAME

    with default_path.open("r") as yaml_file:
        config = GeneratorConfig(**yaml.safe_load(yaml_file))

    if config_name is not None:
        config_path = dir_path / config_name / GENERATOR_FILENAME
        if not config_path.exists():
            raise ConfigNotFoundException(
                f"Configuration {config_path} does not exists."
            )

        with config_path.open("r") as yaml_file:
            config = config.update(**yaml.safe_load(yaml_file))

    return config


def get_generator_path(generator_config: GeneratorConfig) -> Path:
    return Path(__file__).parent.joinpath(generator_config.name)
