from pathlib import Path
from typing import Optional

from kataloger.exceptions.kataloger_configuration_exception import KatalogerConfigurationException


def str_to_path(path_string: str, root_path: Optional[Path] = None) -> Path:
    """
    Converts a string representing a file path into a Path object. It expands user tilde (~) and resolves relative
    paths against a provided base path. It also verifies the existence of the file at the specified path.

    :param path_string: A string representing the file path to be converted.
    :param root_path: An optional base path against which to resolve relative paths. Defaults to None.
    :return: A Path object representing the absolute file path.
    :raise KatalogerConfigurationException: If the resolved path does not point to an existing file.
    """
    path = Path(path_string).expanduser()
    if not path.is_absolute() and root_path:
        path = (root_path / path).resolve()

    if not file_exists(path):
        raise KatalogerConfigurationException(message=f'Incorrect path: "{path_string}".')

    return path


def file_exists(path: Path) -> bool:
    """
    Checks whether a given path exists and is a file.

    :param path: A Path object representing the file path to be checked.
    :returns: True if the path exists and is a file, False otherwise.
    """
    return path.exists() and path.is_file()
