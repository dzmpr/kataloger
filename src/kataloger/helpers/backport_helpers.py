import sys
from pathlib import Path
from typing import Union

from kataloger.exceptions.kataloger_parse_exception import KatalogerParseException


def load_toml(path: Path) -> dict[str, Union[str, dict]]:
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
