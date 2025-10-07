from __future__ import annotations

import tarfile
import zipfile
from pathlib import Path
from re import Match, search
from typing import Literal, Optional

from ..logs import Styles, my_logger
from .files import MyFileValidator


class MyDirValidator:
    NAME_PATTERN: Optional[str] = None
    REQUIRED_FILES: list[type[MyFileValidator]] = []
    REQUIRED_DIRS: list[type[MyDirValidator]] = []
    ALLOWED_FILES: list[type[MyFileValidator]] = []

    def __init__(self, path: str | Path) -> None:
        self.path = path
        self._required_files: list[Path] = []

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, value: str | Path) -> None:
        value = Path(value)
        self._path: Path = value

    @property
    def files(self) -> list[Path]:
        return [item for item in self.path.iterdir() if item.is_file()]

    @property
    def sub_dirs(self) -> list[Path]:
        return [item for item in self.path.iterdir() if item.is_dir()]

    @classmethod
    def add_required_file(cls, value: type[MyFileValidator] | list[type[MyFileValidator]]) -> None:
        if isinstance(value, type) and issubclass(value, MyFileValidator):
            value = [value]
        for file in value:
            my_logger.debug(f'"{file.__name__}" added to "{cls.__name__}.REQUIRED_FILES".')
            cls.REQUIRED_FILES.append(file)

    @classmethod
    def add_required_dir(cls, value: type[MyDirValidator] | list[type[MyDirValidator]]) -> None:
        if isinstance(value, type) and issubclass(value, MyDirValidator):
            value = [value]
        for dir in value:
            my_logger.debug(f'"{dir.__name__}" added to "{cls.__name__}.REQUIRED_DIRS".')
            cls.REQUIRED_DIRS.append(dir)

    def exists(self) -> bool:
        return self.path.is_dir()

    @classmethod
    def name_pattern_check(cls, name: str) -> bool:
        if cls.NAME_PATTERN is None:
            return True
        result: Optional[Match[str]] = search(cls.NAME_PATTERN, name)
        if result is None:
            return False
        return bool(result)

    def required_files_check(self) -> bool:
        if len(self.REQUIRED_FILES) == 0:
            return True
        files_check: list[bool] = []
        self._required_files = []
        for file_validator in self.REQUIRED_FILES:
            result: bool
            path: Optional[Path]
            result, path = file_validator.find(self.files)
            files_check.append(result)
            if result and path is not None:
                self._required_files.append(path)
        if not all(files_check):
            error_files: list[str] = [
                file.__name__
                for file, mask in zip(self.REQUIRED_FILES, files_check)
                if not mask
            ]
            my_logger.error(f'"{self.path}" does not contain {error_files} files.')
            return False
        return True

    def allowed_files_check(self) -> bool:
        if len(self.files) == 0 or len(self.ALLOWED_FILES) == 0:
            return True
        not_allowed_files: list[str] = []
        for file in self.files:
            if file in self._required_files:
                continue
            found = False
            for file_validator in self.ALLOWED_FILES:
                if file_validator.validate(file):
                    found = True
                    break
            if found:
                continue
            not_allowed_files.append(file.name)
        if len(not_allowed_files) == 0:
            my_logger.debug(
                f'All files in {self.path} are allowed for a "{self.__class__.__name__}".',
                Styles.SUCCEED
            )
            return True
        my_logger.error(f'{not_allowed_files} are not valid files for a "{self.__class__.__name__}" in "{self.path}".')
        return False

    def required_dirs_check(self) -> bool:
        if len(self.REQUIRED_DIRS) == 0:
            return True
        dirs_check: list[bool] = [False for _ in self.REQUIRED_DIRS]
        for dir in self.sub_dirs:
            for i, req_dir in enumerate(self.REQUIRED_DIRS):
                if req_dir.name_pattern_check(dir.name):
                    if req_dir(dir).validate():
                        dirs_check[i] = True
                        break
        if not all(dirs_check):
            error_dirs: list[str] = [
                dir.__name__
                for dir, mask in zip(self.REQUIRED_DIRS, dirs_check)
                if not mask
            ]
            my_logger.error(f'"{self.path}" does not contain valid {error_dirs} dirs needed for a "{self.__class__.__name__}".')
            return False
        my_logger.debug(
            f'"{self.path}" contains all "{self.__class__.__name__}.REQUIRED_DIRS".',
            Styles.SUCCEED
        )
        return True

    def validate(self) -> bool:
        if not self.exists():
            my_logger.error(f'"{self.path}" does not exists.')
            return False
        result: bool = True
        result &= self.name_pattern_check(self.path.name)
        result &= self.required_files_check()
        result &= self.allowed_files_check()
        result &= self.required_dirs_check()
        if result:
            my_logger.debug(
                f'"{self.path}" has a valid structure for "{self.__class__.__name__}".',
                Styles.SUCCEED
            )
        else:
            my_logger.error(f'"{self.path}" does not have a valid structure for "{self.__class__.__name__}".')
        return result


def unzip_dir(dir: Path) -> Path:
    if not dir.exists():
        msg: str = f'Path "{dir}" doesn\'t exists.'
        my_logger.error(f'FileExistsError: {msg}')
        raise FileExistsError(msg)
    if dir.is_dir():
        return dir
    suffixes: list[str] = dir.suffixes
    if not suffixes:
        msg: str = f'File has no extension.'
        my_logger.error(f'ValueError: {msg}')
        raise ValueError(msg)
    extension: str = suffixes[-1].lower()
    new_path: Path = dir.parent / dir.stem
    if extension == '.zip':
        _uzip(dir, new_path)
    elif extension in ('.tar', '.gz', '.bz2', '.xz'):
        _utar(dir, new_path)
    else:
        msg: str = f'File extension not supported: "{extension}".'
        my_logger.error(f'ValueError: {msg}')
        raise ValueError(msg)
    return new_path

def _uzip(file: Path, path: Path) -> None:
    with zipfile.ZipFile(file, 'r') as f:
        f.extractall(path)
    my_logger.debug(f'{file.name} extracted in {path}.', Styles.SUCCEED)

def _utar(file: Path, path: Path) -> None:
    modes: dict[str, Literal['r', 'r:gz', 'r:bz2', 'r:xz']] = {
        '.tar': 'r',
        '.gz': 'r:gz',
        '.bz2': 'r:bz2',
        '.xz': 'r:xz'
    }
    mode: str = modes[file.suffixes[-1].lower()]
    with tarfile.open(file, mode) as f:
        f.extractall(path)
    my_logger.debug(f'{file.name} extracted in {path}.', Styles.SUCCEED)
