from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import torch
from astropy.io import fits
from pydantic import ValidationError

from astromorph.app import training
from astromorph.datasets import FitsFilelistDataset
from astromorph.pipeline_01_training import main as training_main
from astromorph.settings import TrainingSettings


class TestTrainingCommand:
    """Test the training command functionality."""

    def test_training_command_with_valid_config(
        self, sample_config_file: Path, sample_filelist: Path
    ) -> None:
        """Test training command with valid configuration file."""
        with patch("astromorph.pipeline_01_training.main") as mock_main:
            training(sample_config_file)
            mock_main.assert_called_once()
            args, kwargs = mock_main.call_args
            assert len(args) == 1
            assert isinstance(args[0], FitsFilelistDataset)
            assert "settings" in kwargs
            assert isinstance(kwargs["settings"], TrainingSettings)

    def test_training_command_loads_config_correctly(
        self, sample_config_file: Path
    ) -> None:
        """Test that configuration is loaded correctly from TOML file."""
        with patch("astromorph.pipeline_01_training.main") as mock_main:
            training(sample_config_file)
            args, kwargs = mock_main.call_args
            settings = kwargs["settings"]
            assert settings.epochs == 2
            assert settings.learning_rate == 1e-4
            assert settings.network_name == "amm"
            assert settings.batch_size == 2
            assert settings.core_limit == 1

    def test_training_command_sets_torch_threads(
        self, sample_config_file: Path
    ) -> None:
        """Test that torch thread count is set correctly."""
        with patch("astromorph.pipeline_01_training.main"):
            with patch("torch.set_num_threads") as mock_set_threads:
                training(sample_config_file)
                mock_set_threads.assert_called_once_with(1)

    def test_training_command_with_invalid_config_file(self, temp_dir: Path) -> None:
        """Test training command with non-existent config file."""
        invalid_config = temp_dir / "nonexistent.toml"
        with pytest.raises(FileNotFoundError):
            training(invalid_config)


class TestTrainingPipeline:
    """Test the training pipeline main function."""

    def test_training_main_basic_functionality(
        self, mock_dataset, training_settings: TrainingSettings
    ) -> None:
        """Test basic functionality of training main function."""
        mock_network = MagicMock()
        mock_trainer = MagicMock()

        with (
            patch("astromorph.pipeline_01_training.DEFAULT_MODELS") as mock_models,
            patch(
                "astromorph.pipeline_01_training.ByolTrainer", return_value=mock_trainer
            ) as mock_trainer_class,
            patch(
                "astromorph.pipeline_01_training.torch.utils.data.random_split",
                side_effect=lambda dataset, lengths, generator: (MagicMock(), MagicMock()),
            ),
            patch(
                "astromorph.pipeline_01_training.DataLoader", return_value=MagicMock()
            ),
            patch("astromorph.pipeline_01_training.os.makedirs"),
            patch("builtins.open", MagicMock()),
        ):

            mock_models.__getitem__.return_value.return_value = mock_network
            training_main(mock_dataset, training_settings)
            mock_trainer_class.assert_called_once()
            mock_trainer.train_model.assert_called_once()

    def test_training_main_device_selection(
        self, mock_dataset, training_settings: TrainingSettings
    ) -> None:
        """Test that device selection works correctly."""
        mock_network = MagicMock()

        with (
            patch("astromorph.pipeline_01_training.DEFAULT_MODELS") as mock_models,
            patch(
                "astromorph.pipeline_01_training.ByolTrainer", return_value=MagicMock()
            ),
            patch(
                "astromorph.pipeline_01_training.torch.utils.data.random_split",
                side_effect=lambda dataset, lengths, generator: (MagicMock(), MagicMock()),
            ),
            patch("astromorph.pipeline_01_training.DataLoader"),
            patch("astromorph.pipeline_01_training.os.makedirs"),
            patch("builtins.open", MagicMock()),
        ):

            mock_models.__getitem__.return_value.return_value = mock_network
            training_main(mock_dataset, training_settings)
            mock_network.to.assert_called_once_with("cpu")

    def test_training_main_creates_saved_models_directory(
        self, mock_dataset, training_settings: TrainingSettings
    ) -> None:
        """Test that saved_models directory is created if it doesn't exist."""
        mock_network = MagicMock()

        with (
            patch("astromorph.pipeline_01_training.DEFAULT_MODELS") as mock_models,
            patch(
                "astromorph.pipeline_01_training.ByolTrainer", return_value=MagicMock()
            ),
            patch(
                "astromorph.pipeline_01_training.torch.utils.data.random_split",
                side_effect=lambda dataset, lengths, generator: (MagicMock(), MagicMock()),
            ),
            patch("astromorph.pipeline_01_training.DataLoader"),
            patch("astromorph.pipeline_01_training.os.path.exists", return_value=False),
            patch("astromorph.pipeline_01_training.os.makedirs") as mock_makedirs,
            patch("builtins.open", MagicMock()),
        ):

            mock_models.__getitem__.return_value.return_value = mock_network
            training_main(mock_dataset, training_settings)
            mock_makedirs.assert_called_with("./saved_models")
            assert mock_makedirs.call_count >= 1

    def test_training_main_with_exponential_lr(
        self, mock_dataset, training_settings: TrainingSettings
    ) -> None:
        """Test training with exponential learning rate scheduler."""
        training_settings.exponential_lr = True
        mock_network = MagicMock()

        with (
            patch("astromorph.pipeline_01_training.DEFAULT_MODELS") as mock_models,
            patch("astromorph.pipeline_01_training.ByolTrainer") as mock_trainer_class,
            patch(
                "astromorph.pipeline_01_training.torch.utils.data.random_split",
                side_effect=lambda dataset, lengths, generator: (MagicMock(), MagicMock()),
            ),
            patch("astromorph.pipeline_01_training.DataLoader"),
            patch("astromorph.pipeline_01_training.os.makedirs"),
            patch("builtins.open", MagicMock()),
        ):

            mock_models.__getitem__.return_value.return_value = mock_network
            mock_trainer_class.return_value = MagicMock()
            training_main(mock_dataset, training_settings)
            call_args = mock_trainer_class.call_args
            assert call_args[1]["lr_scheduler"] is not None


class TestTrainingSettings:
    """Test TrainingSettings validation and functionality."""

    def test_training_settings_validation(self, sample_filelist: Path) -> None:
        """Test that TrainingSettings validates input correctly."""
        settings = TrainingSettings(
            datafile=str(sample_filelist),
            epochs=5,
            network_name="amm",
            network_settings={},
            byol_settings={},
        )
        assert settings.epochs == 5
        assert settings.network_name == "amm"
        assert settings.learning_rate == 5e-6
        assert settings.batch_size == 16

    def test_training_settings_invalid_epochs(self, sample_filelist: Path) -> None:
        """Test that invalid epochs values are rejected."""
        with pytest.raises(ValueError):
            TrainingSettings(
                datafile=str(sample_filelist),
                epochs=0,
                network_name="amm",
                network_settings={},
                byol_settings={},
            )

    def test_training_settings_invalid_gamma(self, sample_filelist: Path) -> None:
        """Test that invalid gamma values are rejected."""
        with pytest.raises(ValueError):
            TrainingSettings(
                datafile=str(sample_filelist),
                epochs=5,
                network_name="amm",
                network_settings={},
                byol_settings={},
                gamma=1.5,
            )

    def test_training_settings_file_validation(self, temp_dir: Path) -> None:
        """Test that TrainingSettings validates file existence."""
        nonexistent_file = temp_dir / "nonexistent.txt"

        with pytest.raises(ValidationError):
            TrainingSettings(
                datafile=str(nonexistent_file),
                epochs=5,
                network_name="amm",
                network_settings={},
                byol_settings={},
            )


class TestFitsFilelistDataset:
    """Test FitsFilelistDataset functionality."""

    def test_fits_dataset_creation_from_file(self, sample_filelist: Path) -> None:
        """Test creating FitsFilelistDataset from file."""
        dataset = FitsFilelistDataset(sample_filelist, stacksize=1)

        assert len(dataset) == 5
        assert len(dataset.filenames) == 5

    def test_fits_dataset_creation_from_list(self, temp_dir: Path) -> None:
        """Test creating FitsFilelistDataset from list of files."""
        file_paths = []
        for i in range(3):
            fits_path = temp_dir / f"test_{i}.fits"
            data = torch.randn(32, 32).numpy().astype(np.float32)
            hdu = fits.PrimaryHDU(data)
            hdu.writeto(fits_path)
            file_paths.append(str(fits_path))
        dataset = FitsFilelistDataset(file_paths, stacksize=1)
        assert len(dataset) == 3
        assert dataset.filenames == file_paths

    def test_fits_dataset_getitem(self, sample_filelist: Path) -> None:
        """Test that __getitem__ returns correct tensor shape."""
        dataset = FitsFilelistDataset(sample_filelist, stacksize=1)
        item = dataset[0]
        assert isinstance(item, torch.Tensor)
        assert len(item.shape) == 4
        assert item.shape[0] == 1
        assert item.shape[1] == 1
