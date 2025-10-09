from __future__ import annotations

from sphinx.application import Sphinx

from sphinxcontrib.kasane.conditions import (
    BuilderCondition,
    BuilderFormatCondition,
)
from sphinxcontrib.kasane.inheritance import MixinDynamicInheritance

__version__ = "0.2.1"


class TranslatorSetUp:
    def __init__(
        self, inheritance: MixinDynamicInheritance, condition: BuilderCondition
    ) -> None:
        self.inheritance = inheritance
        self.condition = condition

    def __call__(self, app: Sphinx) -> None:
        if not self.condition.is_satisfied_by(app.builder):
            return

        builder = app.builder
        translator_class = app.registry.get_translator_class(builder)
        app.set_translator(
            builder.name, self.inheritance(translator_class), override=True
        )


def new_translator_class_for_builder(
    builder_format: str, mixin_class: type, new_class_name: str
):
    condition = BuilderFormatCondition(builder_format)
    inheritance = MixinDynamicInheritance(mixin_class, new_class_name)
    return TranslatorSetUp(inheritance, condition)
