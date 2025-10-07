import logging
from pathlib import Path

from pytest import LogCaptureFixture, fixture, mark, raises

from ...src.filesystem.files import *


@fixture(autouse= True)
def set_caplog_lvl(caplog: LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    caplog.clear()

@fixture
def test_files(tmp_path: Path) -> list[tuple[Path, str, type[MyFileValidator]]]:
    files: list[tuple[Path, str, type[MyFileValidator]]] = []
    if YamlFileValidator.VALID_EXTENSIONS is not None:
        files += [
            (
                tmp_path / f'test_yaml{ext}',
                'name: YAML\nrandom_number: 10\nlist:\n  first: 1\n  second: 2',
                YamlFileValidator
            )
            for ext in YamlFileValidator.VALID_EXTENSIONS
        ]
    if TomlFileValidator.VALID_EXTENSIONS is not None:
        files += [
            (
                tmp_path / f'test_toml{ext}',
                '[data]\n\tname = "TOML"\n\trandom_number = 1.5\n\t',
                TomlFileValidator
            )
            for ext in TomlFileValidator.VALID_EXTENSIONS
        ]
    if ImageFileValidator.VALID_EXTENSIONS is not None:
        files += [
            (tmp_path / f'test_image{ext}', '', ImageFileValidator)
            for ext in ImageFileValidator.VALID_EXTENSIONS
        ]
    if TxtFileValidator.VALID_EXTENSIONS is not None:
        files += [
            (tmp_path / f'test_txt{ext}', '', TxtFileValidator)
            for ext in TxtFileValidator.VALID_EXTENSIONS
        ]
    if ConfigFileValidator.VALID_EXTENSIONS is not None:
        files += [
            (tmp_path / f'test_cfg{ext}', '', ConfigFileValidator)
            for ext in ConfigFileValidator.VALID_EXTENSIONS
        ]
    for path, content, _ in files:
        path.touch()
        path.write_text(content)
    return files


class NameValidator(MyFileValidator):
    NAME_PATTERN = r'^test.*\.yaml$'
    
    ok_names: list[str] = [
        'test_something.yaml'
    ]
    nok_names: list[str] = [
        'test_something,yaml',
        'not.yaml.toml'
    ]


class TestMyFileValidator:
    @staticmethod
    def test_instance() -> None:
        with raises(SyntaxError):
            _ = MyFileValidator()

    @staticmethod
    def test_validate_name() -> None:
        for name in NameValidator.ok_names:
            assert NameValidator.validate_name(name)
        for name in NameValidator.nok_names:
            assert not NameValidator.validate_name(name)

    @staticmethod
    def test_find(
        test_files: list[tuple[Path, str, type[MyFileValidator]]]
    ) -> None:
        assert NameValidator.find([f for f, _, _ in test_files])[0]
        assert NameValidator.find([Path(name) for name in NameValidator.ok_names])[0]
        assert not NameValidator.find([Path(name) for name in NameValidator.nok_names])[0]

    @staticmethod
    def test_validate_default_subclasses(
        test_files: list[tuple[Path, str, type[MyFileValidator]]]
    ) -> None:
        for path, _, validator in test_files:
            assert validator.validate(path)

    @staticmethod
    def test_class_factory() -> None:
        CustomClassPattern: type[MyFileValidator] = my_file_validator_factory(
            class_name= 'CustomClassPattern',
            name_pattern= r'\.txt$',
        )
        CustomClassExtension: type[MyFileValidator] = my_file_validator_factory(
            class_name= 'CustomClassExtension',
            valid_extensions= ['.png'],
        )
        assert issubclass(CustomClassPattern, MyFileValidator)
        assert CustomClassPattern.validate('test.txt', exists= False)
        assert not CustomClassPattern.validate('test.png', exists= False)
        assert not CustomClassPattern.validate('test.xt', exists= False)
        assert CustomClassExtension.validate('test.png', exists= False)
        assert not CustomClassExtension.validate('test.xt', exists= False)


class TestFunctions:
    @staticmethod
    def test_copy(
        test_files: list[tuple[Path, str, type[MyFileValidator]]],
        tmp_path: Path
    ) -> None:
        new_dir: Path = tmp_path / 'new'
        new_dir.mkdir(exist_ok= True)
        copy_files(
            [file for file, _, _ in test_files],
            destiny_dir= new_dir
        )
        base_dir_files: list[str] = [f.name for f in tmp_path.iterdir() if f.is_file()]
        new_dir_files: list[str] = [f.name for f in new_dir.iterdir() if f.is_file()]
        for file in base_dir_files:
            assert file in new_dir_files