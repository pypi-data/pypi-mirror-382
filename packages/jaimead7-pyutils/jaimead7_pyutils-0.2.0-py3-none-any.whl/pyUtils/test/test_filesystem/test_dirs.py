#TODO:
import logging
from pathlib import Path

from pytest import LogCaptureFixture, fixture, mark, raises

from pyUtils import *


@fixture(autouse= True)
def set_caplog_lvl(caplog: LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    caplog.clear()

@fixture(autouse= True)
def create_dir(tmp_path: Path) -> None:
    (tmp_path / 'test').mkdir()
    (tmp_path / 'test' / 'images').mkdir()
    (tmp_path / 'test' / 'labels').mkdir()
    (tmp_path / 'train').mkdir()
    (tmp_path / 'train' / 'images').mkdir()
    (tmp_path / 'train' / 'labels').mkdir()
    (tmp_path / 'validation').mkdir()
    (tmp_path / 'validation' / 'images').mkdir()
    (tmp_path / 'validation' / 'labels').mkdir()
    (tmp_path / 'data.yaml').touch()
    (tmp_path / 'metadata.yaml').touch()


class TestMyDirValidator:
    @staticmethod
    def test_global(tmp_path: Path) -> None:
        class DataYamlFile(YamlFileValidator):
            NAME_PATTERN = r'^data\.yaml$'
        class MetadataYamlFile(YamlFileValidator):
            NAME_PATTERN = r'^metadata\.yaml$'
        class ImageDir(MyDirValidator):
            NAME_PATTERN = r'^images$'
            ALLOWED_FILES: list[type[MyFileValidator]] = [
                ImageFileValidator
            ]
        class LabelsDir(MyDirValidator):
            NAME_PATTERN = r'^labels$'
            ALLOWED_FILES: list[type[MyFileValidator]] = [
                TxtFileValidator
            ]
        class TestDir(MyDirValidator):
            NAME_PATTERN = r'^test$'
            REQUIRED_DIRS: list[type[MyDirValidator]] = [
                ImageDir,
                LabelsDir
            ]
        class TrainDir(MyDirValidator):
            NAME_PATTERN = r'^train$'
            REQUIRED_DIRS: list[type[MyDirValidator]] = [
                ImageDir,
                LabelsDir
            ]
        class ValidationDir(MyDirValidator):
            NAME_PATTERN = r'^validation$'
            REQUIRED_DIRS: list[type[MyDirValidator]] = [
                ImageDir,
                LabelsDir
            ]
        class TrainingDir(MyDirValidator):
            REQUIRED_FILES: list[type[MyFileValidator]] = [
                DataYamlFile
            ]
            ALLOWED_FILES: list[type[MyFileValidator]] = [
                TomlFileValidator
            ]
            REQUIRED_DIRS: list[type[MyDirValidator]] = [
                TestDir,
                TrainDir,
                ValidationDir
            ]
        TrainingDir.add_required_file(MetadataYamlFile)
        dir = TrainingDir(tmp_path)
        assert dir.validate()
