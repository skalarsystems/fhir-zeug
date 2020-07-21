import os
import re
import shutil
import textwrap
from typing import Optional, TextIO, TYPE_CHECKING
from pathlib import Path
from stringcase import snakecase  # type: ignore

from jinja2 import Environment, PackageLoader, TemplateNotFound
from jinja2.filters import environmentfilter
from .logger import logger

if TYPE_CHECKING:
    from .fhirspec import FHIRSpec


class FHIRRenderer:
    """ Superclass for all renderer implementations.
    """

    def __init__(self, spec: "FHIRSpec"):
        self.spec = spec
        self.generator_config = spec.generator_config
        self.jinjaenv = Environment(
            loader=PackageLoader(
                self.generator_config.module, self.generator_config.template.source,
            ),
            extensions=["jinja2.ext.do"],  # Allow the "do" statement in Jinja
        )
        self.jinjaenv.filters["wordwrap"] = do_wordwrap
        self.jinjaenv.filters["snake_case"] = snakecase

    def render(self, f_out: Optional[TextIO] = None) -> None:
        """ The main rendering start point, for subclasses to override.
        """
        raise Exception("Cannot use abstract superclass' `render` method")

    def do_render(
        self,
        data,
        template_name: str,
        target_path: Optional[Path] = None,
        f_out: Optional[TextIO] = None,
    ) -> None:
        """ Render the given data using a Jinja2 template, writing to the file
        at the target path.

        :param template_name: The Jinja2 template to render
        :param target_path: Output path
        """

        try:
            template = self.jinjaenv.get_template(template_name)
        except TemplateNotFound:
            logger.error(
                f'Template "{template_name}" not found in "{self.generator_config.template.source}", cannot render'
            )
            return

        if target_path:
            dirpath = os.path.dirname(target_path)

            if not os.path.isdir(dirpath):
                os.makedirs(dirpath)

            f_out = open(target_path, "w")

        if f_out is None:
            raise ValueError("No target filepath or file object provided")

        logger.info("Writing {}".format(target_path))
        rendered = template.render(data)
        f_out.write(rendered)


class FHIRStructureDefinitionRenderer(FHIRRenderer):
    """ Write classes for a profile/structure-definition.
    """

    def copy_files(self, target_dir, f_out):
        """ Copy base resources to the target location, according to config.
        """
        for manual_profile in self.generator_config.manual_profiles:
            origpath = manual_profile.origpath
            if origpath and origpath.exists():
                if f_out:
                    with origpath.open("r") as f_in:
                        shutil.copyfileobj(f_in, f_out)
                else:
                    tgt = target_dir / origpath.name
                    logger.info(f"Copying manual profiles in {tgt.name} to {tgt}")
                    shutil.copyfile(origpath, tgt)

    def render(self, f_out):
        self.copy_files(None, f_out)

        classes = self.get_classes_to_render()
        for clazz in classes:
            data = {"clazz": clazz}
            source_path = self.generator_config.template.resource_source
            self.do_render(data, source_path, f_out=f_out)

    def get_classes_to_render(self):
        """Recursively fetch all classes to render."""
        derive_graph = {}

        # sort according to derive
        # MoneyQuantity name changes to Quantity
        for profile in self.spec.writable_profiles():
            classes = profile.writable_classes()
            for cl in classes:
                # deps[cl.name] = cl.superclass_name
                derive_graph.setdefault(cl.superclass_name, []).append(cl)

        classes = []
        work_stack = [
            "FHIRAbstractBase",
            "FHIRAbstractResource",
        ]

        while work_stack:
            current = work_stack.pop()
            for elm in derive_graph.get(current, []):
                work_stack.append(elm.name)
                if elm not in classes:
                    classes.append(elm)

        return classes


class FHIRValueSetRenderer(FHIRRenderer):
    """ Write ValueSet and CodeSystem contained in the FHIR spec.
    """

    def render(self, f_out):
        systems = [v for k, v in self.spec.codesystems.items()]
        for system in sorted(systems, key=lambda x: x.name):
            if not system.generate_enum:
                continue

            data = {
                "info": self.spec.info,
                "system": system,
            }
            source_path = self.generator_config.template.codesystems_source
            self.do_render(data, source_path, f_out=f_out)


# There is a bug in Jinja's wordwrap (inherited from `textwrap`) in that it
# ignores existing linebreaks when applying the wrap:
# https://github.com/mitsuhiko/jinja2/issues/175
# Here's the workaround:
@environmentfilter
def do_wordwrap(environment, s, width=79, break_long_words=True, wrapstring=None):
    """
    Return a copy of the string passed to the filter wrapped after
    ``79`` characters.  You can override this default using the first
    parameter.  If you set the second parameter to `false` Jinja will not
    split words apart if they are longer than `width`.
    """
    if not s:
        return s

    if not wrapstring:
        wrapstring = environment.newline_sequence

    accumulator = []
    # Workaround: pre-split the string on \r, \r\n and \n
    for component in re.split(r"\r\n|\n|\r", s):
        # textwrap will eat empty strings for breakfirst. Therefore we route them around it.
        if len(component) == 0:
            accumulator.append(component)
            continue
        accumulator.extend(
            textwrap.wrap(
                component,
                width=width,
                expand_tabs=False,
                replace_whitespace=False,
                break_long_words=break_long_words,
            )
        )
    return wrapstring.join(accumulator)
