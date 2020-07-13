from pathlib import Path

from fhirzeug.generator import generate
from fhirzeug.fhirspec import FHIRSpec


def test_write(spec: FHIRSpec, tmp_path: Path):
    spec.generator_config.output_directory.destination = tmp_path
    spec.generator_config.output_file.destination = Path("output.py")
    generate(spec)
    assert tmp_path.joinpath("output.py").is_file()
