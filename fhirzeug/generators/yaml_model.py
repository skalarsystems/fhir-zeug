from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel


class CopyTarget(BaseModel):
    """A target to copy a file.
    
    Attributes:
        destination: path where the file should copied to
    """

    destination: Path


class Template(BaseModel):
    """not in use yet"""

    destination: Path
    input: Path
    output: Path
    variables: List[str]


class GeneratorConfig(BaseModel):
    """Config for the generator. Each Generator for each language has one.
    
    Attributes:
        copy_examples: Target of where the 
        templates: *not in used yes*
        output_file: Where the generate file will be pushed.
    """

    copy_examples: Optional[CopyTarget]
    templates: Optional[List[Template]]
    output_file: Path
