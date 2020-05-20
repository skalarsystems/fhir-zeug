from pathlib import Path
import shutil

from .fhirspec import FHIRSpec
from . import fhirrenderer
from .generators.yaml_model import GeneratorConfig


def generate(spec: FHIRSpec, output_directory: Path, generator_config: GeneratorConfig):
    """Generates code based on the spec and the generator.
    
    
    Args:
        spec: A parsed specification.
        output_directory: The directory where the output goes to.
    """
    output_directory.mkdir(exist_ok=True)
    generator_path = Path(spec.settings.__file__).parent

    # copy examples if configured
    if generator_config.copy_examples is not None:
        dest_directory = output_directory.joinpath(
            generator_config.copy_examples.destination
        )
        dest_directory.mkdir(parents=True, exist_ok=True)
        for source_path in spec.directory.glob("*-example.json"):
            dest_path = dest_directory.joinpath(source_path.name)
            shutil.copy2(source_path, dest_path)

    # copy static files
    shutil.copytree(
        generator_path.joinpath("static_files"), output_directory, dirs_exist_ok=True,
    )

    # configureable templates
    if spec.settings.write_resources:
        with output_directory.joinpath(generator_config.output_file).open("w") as f_out:
            with generator_path.joinpath("templates/resource_header.py").open(
                "r"
            ) as f_in:
                shutil.copyfileobj(f_in, f_out)
            value_set_renderer = fhirrenderer.FHIRValueSetRenderer(
                spec, spec.settings, spec.generator_module
            )
            value_set_renderer.render(f_out)

            renderer = fhirrenderer.FHIRStructureDefinitionRenderer(
                spec, spec.settings, spec.generator_module
            )
            renderer.render(f_out)

            with generator_path.joinpath("templates/resource_footer.py").open(
                "r"
            ) as f_in:
                shutil.copyfileobj(f_in, f_out)
