import pytest
from pathlib import Path

from fhirzeug.generators import load_config, ConfigNotFoundException


def test_load_config():
    with pytest.raises(ConfigNotFoundException):
        config = load_config("do_not_exists")

    config = load_config()
    assert config.name == "default"

    config = load_config("python_pydantic")
    assert config.name == "python_pydantic"
    assert config.download_directory.destination == Path("downloads")
