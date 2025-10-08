from typing import ClassVar

import pytest

from spl_core.test_utils.spl_build import SplBuild


class Test_EnglishVariant:
    variant: str = "EnglishVariant"
    components: ClassVar[list[str]] = ["src/greeter"]

    @pytest.mark.unittests
    def test_unittests(self) -> None:
        # Arrange
        spl_build: SplBuild = SplBuild(variant=self.variant, build_kit="test", build_type="Debug", target="unittests")

        # Act
        result = spl_build.execute()

        # Assert
        assert result == 0, "Building unittests failed"
        for artifact in spl_build.get_components_artifacts(self.components):
            assert artifact.exists(), f"Artifact {artifact} does not exist"

    @pytest.mark.reports
    def test_reports(self) -> None:
        # Arrange
        spl_build: SplBuild = SplBuild(variant=self.variant, build_kit="test", build_type="Debug", target="reports")

        # Act
        result = spl_build.execute()

        # Assert
        assert result == 0, "Building reports failed"
        for artifact in spl_build.get_components_artifacts(self.components):
            assert artifact.exists(), f"Artifact {artifact} does not exist"

    @pytest.mark.build
    @pytest.mark.parametrize(
        ("build_type"),
        [
            pytest.param("Debug", marks=pytest.mark.debug),
            pytest.param("Release", marks=pytest.mark.release),
        ],
    )
    def test_build(self, build_type: str) -> None:
        # Arrange
        spl_build: SplBuild = SplBuild(variant=self.variant, build_kit="prod", build_type=build_type, target="all")

        # Act
        result = spl_build.execute()

        # Assert
        assert result == 0, "Building failed"
        for artifact in [spl_build.build_dir / "main.exe", *spl_build.get_variant_artifacts()]:
            assert artifact.exists(), f"Artifact {artifact} does not exist"
