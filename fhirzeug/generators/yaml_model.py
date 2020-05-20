from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel


class CopyTarget(BaseModel):
    destination: Path


class Template(BaseModel):
    destination: Path
    input: Path
    output: Path
    variables: List[str]


class GeneratorConfig(BaseModel):
    copy_examples: Optional[CopyTarget]
    templates: Optional[List[Template]]
    output_file: Path
