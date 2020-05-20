import sys
import importlib
from pathlib import Path

import typer
import yaml

from . import fhirspec, logger
from .specificationcache import SpecificationCache
from .generators.yaml_model import GeneratorConfig


app = typer.Typer()


def load_generator_config(path: Path) -> GeneratorConfig:
    return GeneratorConfig(**yaml.load(path.open("r")))


@app.command()
def main(
    force_download: bool = False,
    dry_run: bool = False,
    load_only: bool = False,
    generator: str = "python_pydantic",
    output_directory: Path = Path("output"),
    download_cache: Path = Path("./downloads"),
):
    """Download and parse FHIR resource definitions."""

    logger.setup_logging()

    generator_module = f"fhirzeug.generators.{generator}.settings"

    # todo make this disappear and replace it with
    generator_settings = importlib.import_module(generator_module)
    generator_path = Path(generator_settings.__file__).parent
    generator_config = load_generator_config(generator_path.joinpath("generator.yaml"))

    generator_settings.tpl_resource_target = str(output_directory)

    # assure we have all files
    loader = SpecificationCache(generator_settings.specification_url, download_cache)
    loader.sync(force_download=force_download)

    # parse
    if not load_only:
        spec = fhirspec.FHIRSpec(loader.cache_dir, generator_settings, generator_module)
        if not dry_run:
            spec.write(output_directory, generator_config)


if __name__ == "__main__":
    app()
