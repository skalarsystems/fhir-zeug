from pathlib import Path

from fhirzeug.generator import generate
from fhirzeug.fhirspec import FHIRSpec
from fhirzeug.generators.yaml_model import GeneratorConfig


def test_write(spec: FHIRSpec, tmp_path: Path):

    generator_config = GeneratorConfig(output_file=Path("output.py"))
    generate(spec, tmp_path, generator_config)

    assert tmp_path.joinpath("output.py").is_file()
