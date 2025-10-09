from sphinxcontrib.kasane.inheritance import MixinDynamicInheritance


class TestMixinDynamicInheritance:
    def test_create_new_class(self) -> None:
        class AwesomeMixin: ...  # NOQA: E701

        class SomeClass: ...  # NOQA: E701

        sut = MixinDynamicInheritance(AwesomeMixin, "AwesomeNewClass")
        actual = sut(SomeClass)

        assert actual.__name__ == "AwesomeNewClass"
        assert issubclass(actual, AwesomeMixin)
        assert issubclass(actual, SomeClass)
