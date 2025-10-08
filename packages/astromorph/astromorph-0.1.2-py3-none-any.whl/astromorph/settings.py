import os
from typing import Annotated, Any

from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator


def path_exists(filename: str) -> str:
    assert os.path.exists(filename), f"{filename} does not exist"
    return filename


def is_file(filename: str) -> str:
    assert os.path.isfile(filename), f"{filename} is not a file"
    return filename


FileName = Annotated[str, AfterValidator(path_exists), AfterValidator(is_file)]


class FileSettings(BaseModel):
    datafile: FileName
    data_settings: dict[str, Any] = Field(default={})


class TrainingSettings(FileSettings):
    epochs: int = Field(default=10, gt=0)
    network_name: str
    network_settings: dict[str, Any]
    byol_settings: dict[str, Any]
    core_limit: int = Field(default=0, ge=0)
    learning_rate: float = Field(default=5e-6)
    exponential_lr: bool = Field(default=False)
    gamma: float = Field(default=0.99, gt=0, lt=1)
    batch_size: int = Field(default=16, gt=0)


class InferenceSettings(FileSettings):
    trained_network_name: FileName
    export_to_csv: bool = Field(default=False)
