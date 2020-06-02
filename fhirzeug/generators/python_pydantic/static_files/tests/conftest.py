from pathlib import Path


def pytest_generate_tests(metafunc):
    examples_root = Path(__file__).parent.joinpath("examples")
    metafunc.parametrize(
        "fhir_file",
        examples_root.iterdir(),
        ids=(path.name for path in examples_root.iterdir()),
    )
