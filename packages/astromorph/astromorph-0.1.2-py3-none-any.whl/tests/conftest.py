import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import torch
from astropy.io import fits

from astromorph.settings import InferenceSettings, TrainingSettings


@pytest.fixture
def temp_dir() -> Path:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_fits_file(temp_dir: Path) -> Path:
    """Create a sample FITS file for testing."""
    fits_path = temp_dir / "sample.fits"
    data = np.random.rand(64, 64).astype(np.float32)
    hdu = fits.PrimaryHDU(data)
    hdu.writeto(fits_path)

    return fits_path


@pytest.fixture
def sample_filelist(temp_dir: Path, sample_fits_file: Path) -> Path:
    """Create a sample filelist for testing."""
    filelist_path = temp_dir / "filelist.txt"
    fits_files = []
    for i in range(5):
        fits_path = temp_dir / f"sample_{i}.fits"
        data = np.random.rand(64, 64).astype(np.float32)
        hdu = fits.PrimaryHDU(data)
        hdu.writeto(fits_path)
        fits_files.append(str(fits_path))

    with open(filelist_path, "w") as f:
        for file_path in fits_files:
            f.write(f"{file_path}\n")

    return filelist_path


@pytest.fixture
def sample_config_file(temp_dir: Path, sample_filelist: Path) -> Path:
    """Create a sample configuration file for testing."""
    config_path = temp_dir / "config.toml"
    # Create a dummy model file for inference config
    model_file = temp_dir / "dummy_model.pt"
    model_file.touch()

    config_content = f"""datafile = "{sample_filelist}"
trained_network_name = "{model_file}"
export_to_csv = false
epochs = 2
learning_rate = 1e-4
exponential_lr = false
gamma = 0.99
network_name = "amm"
core_limit = 1
batch_size = 2

[network_settings]
# Default settings for AstroMorphologyModel

[data_settings]
stacksize = 1

[byol_settings]
representation_size = 64
projection_size = 32
projection_hidden_size = 128
use_momentum = true
"""

    with open(config_path, "w") as f:
        f.write(config_content)

    return config_path


@pytest.fixture
def training_settings(sample_filelist: Path) -> TrainingSettings:
    """Create a TrainingSettings instance for testing."""
    return TrainingSettings(
        datafile=str(sample_filelist),
        epochs=1,
        network_name="amm",
        network_settings={},
        byol_settings={
            "representation_size": 64,
            "projection_size": 32,
            "projection_hidden_size": 128,
            "use_momentum": True,
        },
        core_limit=1,
        learning_rate=1e-4,
        exponential_lr=False,
        gamma=0.99,
        batch_size=2,
        data_settings={"stacksize": 1},
    )


@pytest.fixture
def mock_dataset():
    """Create a robust mock dataset for testing."""
    dataset = MagicMock()
    
    # Create multiple sample tensors for a more realistic dataset
    mock_tensors = [torch.randn(1, 1, 64, 64) for _ in range(10)]
    dataset.__len__ = MagicMock(return_value=10)
    
    # Make __getitem__ return different tensors based on index
    def mock_getitem(index):
        if isinstance(index, int) and 0 <= index < 10:
            return mock_tensors[index % len(mock_tensors)]
        return mock_tensors[-1]  # fallback
    
    dataset.__getitem__ = MagicMock(side_effect=mock_getitem)
    
    # Add methods needed for inference testing
    dataset.get_all_items.return_value = mock_tensors
    dataset.get_object_property.return_value = [f"object{i}" for i in range(10)]
    dataset.filenames = [f"file{i}.fits" for i in range(10)]

    return dataset


@pytest.fixture
def mock_byol_trainer():
    """Create a mock ByolTrainer for testing."""
    trainer = MagicMock()
    trainer.train_model = MagicMock()
    return trainer


@pytest.fixture(autouse=True)
def mock_torch_cuda():
    """Mock torch.cuda to always return False for consistent testing."""
    with patch("torch.cuda.is_available", return_value=False):
        with patch("torch.backends.mps.is_available", return_value=False):
            yield


@pytest.fixture
def inference_settings(sample_filelist: Path, temp_dir: Path) -> InferenceSettings:
    """Create an InferenceSettings instance for testing."""
    model_file = temp_dir / "model.pt"
    model_file.touch()

    return InferenceSettings(
        datafile=str(sample_filelist),
        trained_network_name=str(model_file),
        export_to_csv=False,
    )


@pytest.fixture
def mock_settings(temp_dir):
    """Create mock settings for testing."""
    from unittest.mock import MagicMock

    model_file = temp_dir / "model.pt"
    model_file.touch()

    mock_settings_instance = MagicMock()
    mock_settings_instance.data_settings = {}
    mock_settings_instance.trained_network_name = str(model_file)
    mock_settings_instance.export_to_csv = False
    return mock_settings_instance


@pytest.fixture
def mock_config_dict(temp_dir, sample_filelist):
    """Create mock config dictionary for testing."""
    model_file = temp_dir / "config_model.pt"
    model_file.touch()

    return {
        "datafile": str(sample_filelist),
        "trained_network_name": str(model_file),
        "export_to_csv": False,
    }


@pytest.fixture(autouse=True)
def mock_logger():
    """Mock loguru logger to avoid file I/O during tests."""
    with patch("loguru.logger") as mock_logger:
        yield mock_logger
