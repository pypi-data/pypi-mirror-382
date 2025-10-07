from pathlib import Path
from re import Match, search
from shutil import copy2
from typing import Any, Callable, Optional

import tomli
import yaml

from ..logs import Styles, my_logger
from ..no_instantiable import NoInstantiable


class MyFileValidator(NoInstantiable):
    NAME_PATTERN: Optional[str] = None
    VALID_EXTENSIONS: Optional[list[str]] = None

    @classmethod
    def validate_name(cls, name: str) -> bool:
        if cls.NAME_PATTERN is None:
            return True
        result: Optional[Match[str]] = search(cls.NAME_PATTERN, name)
        if result is None:
            return False
        return bool(result)

    @staticmethod
    def validate_content(path: str | Path) -> bool:
        #This should be override in derivated classes.
        return True

    @classmethod
    def has_valid_extension(cls, path: Path) -> bool:
        if cls.VALID_EXTENSIONS is None:
            return True
        return path.suffix in cls.VALID_EXTENSIONS

    @classmethod
    def find(cls, paths: list[Path]) -> tuple[bool, Optional[Path]]:
        for path in paths:
            if cls.validate_name(path.name):
                my_logger.debug(
                    f'"{cls.NAME_PATTERN}" found in "{paths[0].parent}".',
                    Styles.SUCCEED
                )
                return (True, path)
        my_logger.error(f'"{cls.NAME_PATTERN}" not found in "{paths[0].parent}".')
        return (False, None)

    @classmethod
    def validate(cls, path: str | Path, exists: bool = True) -> bool:
        if isinstance(path, str):
            path = Path(path)
        if not cls.validate_name(path.name):
            my_logger.error(f'"{path}" is not a valid name for "{cls.__name__}".')
            return False
        if not cls.has_valid_extension(path):
            my_logger.error(f'"{path}" has not a valid extension for "{cls.__name__}".')
            return False
        if exists:
            if path.is_file():
                if not cls.validate_content(path):
                    my_logger.error(f'"{path}" has not a valid content for "{cls.__name__}".')
                    return False
            else:
                my_logger.error(f'"{path}" is not a file.')
                return False
        my_logger.debug(
            f'"{path}" is valid for "{cls.__name__}".',
            Styles.SUCCEED
        )
        return True


class YamlFileValidator(MyFileValidator):
    VALID_EXTENSIONS: Optional[list[str]] = [
        '.yaml',
        '.yml'
    ]

    @staticmethod
    def validate_content(path: str | Path) -> bool:
        if isinstance(path, str):
            path = Path(path)
        try:
            if path.is_file():
                with open(path, 'r') as f:
                    _: Any = yaml.safe_load(f)
            return True
        except:
            return False


class TomlFileValidator(MyFileValidator):
    VALID_EXTENSIONS: Optional[list[str]] = [
        '.toml'
    ]

    @staticmethod
    def validate_content(path: str | Path) -> bool:
        if isinstance(path, str):
            path = Path(path)
        try:
            if path.is_file():
                with open(path, 'rb') as f:
                    _: Any = tomli.load(f)
            return True
        except:
            return False


class ImageFileValidator(MyFileValidator):
    VALID_EXTENSIONS: Optional[list[str]] = [
        '.png',
        '.jpg',
        '.jpeg',
        '.tif',
        '.tiff',
        '.gif',
        '.bmp',
        '.ico',
        '.svg'
    ]


class TxtFileValidator(MyFileValidator):
    VALID_EXTENSIONS: Optional[list[str]] = [
        '.txt'
    ]


class ConfigFileValidator(MyFileValidator):
    VALID_EXTENSIONS: Optional[list[str]] = [
        '.txt',
        '.ini',
        '.yaml',
        '.yml',
        '.toml'
    ]


def my_file_validator_factory(
    class_name: str,
    name_pattern: Optional[str] = None,
    valid_extensions: Optional[list[str]] = None,
    validate_content_func: Callable[[Path], bool] = lambda _: True
) -> type[MyFileValidator]:
    """
    def validate_toml(path: str | Path) -> bool:
        ...
        return True

    TomlFileFactory: type[MyFileValidator] = my_file_validator_factory(
        'TomlFile',
        r'toml$',
        validate_content_func= validate_toml
    )
    """
    if name_pattern is not None:
        name_pattern = f'{name_pattern}'
    if valid_extensions is not None:
        valid_extensions = valid_extensions.copy()
    return type(
        class_name,
        (MyFileValidator, ),
        {
            'NAME_PATTERN': name_pattern,
            'VALID_EXTENSIONS': valid_extensions,
            'validate_content': validate_content_func
        }
    )

def copy_files(
    files_list: list[Path],
    destiny_dir: Path,
    new_names: Optional[list[str]] = None
) -> None:
    if not destiny_dir.is_dir():
        msg: str = f'"{destiny_dir}" does not exists.'
        my_logger.error(f'NotADirectoryError: {msg}')
        raise NotADirectoryError(msg)
    if new_names is None:
        new_names = [file.name for file in files_list]
    destiny_files: list[Path] = [destiny_dir / new_name for new_name in new_names]
    for source, destiny in zip(files_list, destiny_files):
        if source.is_file():
            copy2(source, destiny)
            my_logger.debug(f'"{source.name}" copied to "{destiny}".', Styles.SUCCEED)
        else:
            my_logger.warning(f'"{source}" won\'t be copied. File doesn\'t exists.')
