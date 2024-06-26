from pathlib import Path

import pytest


@pytest.fixture(name="tmp_catalog")
def create_temp_catalog(tmp_path: Path) -> Path:
    catalog_path: Path = tmp_path / "temp.versions.toml"
    catalog_path.touch()
    return catalog_path


@pytest.fixture(name="tmp_conf")
def create_temp_configuration(tmp_path: Path) -> Path:
    configuration_path: Path = tmp_path / "temp.configuration.toml"
    configuration_path.touch()
    return configuration_path
