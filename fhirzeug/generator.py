import shutil

from .fhirspec import FHIRSpec
from . import fhirrenderer
from .generators import get_generator_path


def generate(spec: FHIRSpec):
    """Generates code based on the spec and the generator.

    Args:
        spec: A parsed specification.
    """
    generator_config = spec.generator_config
    output_directory = generator_config.output_directory.destination
    output_directory.mkdir(exist_ok=True)
    generator_path = get_generator_path(generator_config)

    # Copy examples
    dest_directory = output_directory.joinpath(
        generator_config.copy_examples.destination
    )
    dest_directory.mkdir(parents=True, exist_ok=True)
    for source_path in spec.directory.glob("*-example.json"):
        dest_path = dest_directory.joinpath(source_path.name)
        shutil.copy2(source_path, dest_path)

    # Copy static files
    shutil.copytree(
        generator_path.joinpath("static_files"), output_directory, dirs_exist_ok=True,
    )

    # Generate main file
    if generator_config.template.generate_code:
        dest_filepath = output_directory / generator_config.output_file.destination
        with dest_filepath.open("w") as f_out:
            header_filepath = generator_path / "templates/resource_header.py"
            custom_validators_filepath = (
                generator_path / "templates/resource_custom_validators.py"
            )
            footer_filepath = generator_path / "templates/resource_footer.py"

            # Copy Header
            with header_filepath.open("r") as f_in:
                shutil.copyfileobj(f_in, f_out)

            # Render Enums
            fhirrenderer.FHIRValueSetRenderer(spec).render(f_out)

            # Render Resources
            fhirrenderer.FHIRStructureDefinitionRenderer(spec).render(f_out)

            # Copy custom validators
            with custom_validators_filepath.open("r") as f_in:
                shutil.copyfileobj(f_in, f_out)

            # Copy Footer
            with footer_filepath.open("r") as f_in:
                shutil.copyfileobj(f_in, f_out)
