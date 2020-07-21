import typer
from pathlib import Path

from . import fhirspec, logger
from .specificationcache import SpecificationCache
from .generator import generate
from .generators import load_config

app = typer.Typer()


@app.command()
def main(
    force_download: bool = False,
    dry_run: bool = False,
    load_only: bool = False,
    generator: str = "python_pydantic",
    output_directory: Path = Path("output"),  # noqa: B008
    download_directory: Path = Path("./downloads"),  # noqa: B008
):
    """Download and parse FHIR resource definitions."""

    logger.setup_logging()

    generator_config = load_config(generator)
    generator_config.output_directory.destination = output_directory
    generator_config.download_directory.destination = download_directory

    # assure we have all files
    loader = SpecificationCache(
        generator_config.specification_url,
        generator_config.download_directory.destination,
    )
    loader.sync(force_download=force_download)

    # parse
    if not load_only:
        spec = fhirspec.FHIRSpec(loader.cache_dir, generator_config)
        if not dry_run:
            generate(spec)


if __name__ == "__main__":
    app()
