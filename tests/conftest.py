from pathlib import Path

import pytest

from fhirzeug.specificationcache import SpecificationCache
from fhirzeug.fhirspec import FHIRSpec
from fhirzeug.generators import load_config
from fhirzeug.generators.yaml_model import GeneratorConfig


@pytest.fixture(scope="session")
def specification_config() -> GeneratorConfig:
    """A spec cache of r4"""

    return load_config("python_pydantic")


@pytest.fixture(scope="session")
def specification_cache() -> SpecificationCache:
    """A spec cache of r4"""
    cache = SpecificationCache("http://hl7.org/fhir/R4", Path("downloads"))
    cache.sync()
    return cache


@pytest.fixture(scope="session")
def spec(
    specification_cache: SpecificationCache, specification_config: GeneratorConfig
) -> FHIRSpec:
    return FHIRSpec(specification_cache.cache_dir, specification_config)
