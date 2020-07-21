from pathlib import Path
from typing import List, Dict

from pydantic import BaseModel


class Target(BaseModel):
    """A target to copy a file.

    Attributes:
        destination: path where the file should copied to
    """

    destination: Path


class Template(BaseModel):
    """Configuration to find templates.

    Attributes:
        codesystems_source: Source template to generate enums
        generate_code: Whether code generation must be executed
        resource_source: Source template to generate resources
        source: In which directory to find templates
    """

    codesystems_source: str
    generate_code: bool
    resource_source: str
    source: str


class ManualProfile(BaseModel):
    """A profile that is manually defined.

    Attributes:
        contains: list of attributes for the profile
        module: module name
        origpath: path to the template to use
    """

    contains: List[str]
    module: str
    origpath: Path


class NamingRules(BaseModel):
    """Naming rules to apply to generate classes.

    Attributes:
        backbone_class_adds_parent: Weither to prepend parent name to a backbone class
        camelcase_classes: Weither to camelcase all classes names
        camelcase_enums: Weither to camelcase all enums names
        resource_modules_lowercase: Weither to lowercase all module paths
    """

    backbone_class_adds_parent: bool
    camelcase_classes: bool
    camelcase_enums: bool
    resource_modules_lowercase: bool


class MappingRules(BaseModel):
    """Mapping rules to apply to generate classes.

    Attributes:
        classmap: Which class names to map to resources and elements
        replacemap: Classes to be replaced with different ones at resource rendering time
        natives: Which class names are native to the language (or can be treated this way)
        jsonmap: Which classes are to be expected from JSON decoding
        jsonmap_default: Which class if class_name is not recognized
        reservedmap: Properties that need to be renamed because of language keyword conflicts
        enum_map: For enum codes where a computer just cannot generate reasonable names
        enum_namemap: If you want to give specific names to enums based on their URI
        enum_ignore: If certain CodeSystems don't need to generate an enum
    """

    classmap: Dict[str, str] = {}
    replacemap: Dict[str, str] = {}
    natives: List[str] = []
    jsonmap: Dict[str, str] = {}
    jsonmap_default: str
    reservedmap: Dict[str, str] = {}
    enum_map: Dict[str, str] = {}
    enum_namemap: Dict[str, str] = {}
    enum_ignore: Dict[str, str] = {}


class GeneratorConfig(BaseModel):
    """Config for the generator. Each Generator for each language has one.

    Attributes:
        copy_examples: Target of where the tests will be copied
        default_base: Default base model to use depending on the type of the class to generate
        download_directory: Target of where the specification will be downloaded
        manual_profiles: Profile to generate manually
        mapping_rules: Mapping rules to generate classes
        module: Generator module location
        name: Generator name
        naming_rules: Naming rules to generate classes
        output_file: Where the generated file will be pushed (within output_directory)
        output_directory: Directory where the generated module will be pushed
        specification_url: URL where to find specifications
        template: Configuration to find templates
    """

    copy_examples: Target
    default_base: Dict[str, str]
    download_directory: Target
    manual_profiles: List[ManualProfile]
    mapping_rules: MappingRules
    module: str
    name: str
    naming_rules: NamingRules
    output_file: Target
    output_directory: Target
    specification_url: str
    template: Template

    def update(self, **kwargs) -> "GeneratorConfig":
        """Generate a new GeneratorConfig object with updated values.
        """
        attrs = self.dict()
        attrs.update(kwargs)
        return GeneratorConfig(**attrs)
