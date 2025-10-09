from unittest.mock import MagicMock

from sphinx.builders import Builder

from sphinxcontrib.kasane.conditions import (
    BuilderFormatCondition,
    BuilderNameCondition,
)


class TestBuilderFormatCondition:
    def test_satisfied(self):
        html_format_builder = MagicMock(spec=Builder)
        html_format_builder.format = "html"

        sut = BuilderFormatCondition("html")

        assert sut.is_satisfied_by(html_format_builder)

    def test_not_satisfied(self):
        not_html_format_builder = MagicMock(spec=Builder)
        not_html_format_builder.format = "text"

        sut = BuilderFormatCondition("html")

        assert not sut.is_satisfied_by(not_html_format_builder)


class TestBuilderNameCondition:
    def test_satisfied(self):
        singlehtml_builder = MagicMock(spec=Builder)
        singlehtml_builder.name = "singlehtml"

        sut = BuilderNameCondition("singlehtml")

        assert sut.is_satisfied_by(singlehtml_builder)

    def test_not_satisfied(self):
        html_builder = MagicMock(spec=Builder)
        html_builder.name = "html"

        sut = BuilderNameCondition("singlehtml")

        assert not sut.is_satisfied_by(html_builder)
