import sys
from pathlib import Path
from typing import Dict, Union

from kataloger import package_name
from kataloger.exceptions.kataloger_parse_exception import KatalogerParseException


def remove_suffix(string: str, suffix: str) -> str:
    if sys.version_info < (3, 9):
        if suffix and string.endswith(suffix):
            return string[:-len(suffix)]

        return string

    return string.removesuffix(suffix)


def get_package_file(filename: str) -> Path:
    if sys.version_info < (3, 9):
        from importlib_resources import as_file, files
    else:
        from importlib.resources import as_file, files

    with as_file(files(package_name).joinpath(filename)) as path:
        return path


def load_toml(path: Path) -> Dict[str, Union[str, Dict]]:
    if sys.version_info < (3, 11):
        import tomli as tomllib
        from tomli import TOMLDecodeError
    else:
        import tomllib
        from tomllib import TOMLDecodeError

    with Path.open(path, mode="rb") as file:
        try:
            return tomllib.load(file)
        except TOMLDecodeError as parse_error:
            message = f"Can't parse TOML in \"{path.name}\"."
            raise KatalogerParseException(message) from parse_error
