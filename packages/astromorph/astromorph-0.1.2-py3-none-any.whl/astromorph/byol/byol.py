from copy import deepcopy
from typing import Any, Callable, Optional, Union

import torch
from loguru import logger
from torch import nn
from torch.nn.functional import normalize
from torchvision import transforms

from .mlp import MultiLayerPerceptron
from .netwrapper import NetWrapper


def cosine_loss(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Cosine loss function.

    Args:
        x: predicted tensor
        y: target tensor

    Returns:
        Cosine loss tensor
    """
    x = normalize(x, dim=-1, p=2)
    y = normalize(y, dim=-1, p=2)

    result: torch.Tensor = 2 - 2 * (x * y).sum(dim=-1)
    return result


class BYOL(nn.Module):
    """Bootstrap Your Own Latent estimator.

    Attributes:
        augment_function: augmentation function to create different images
        hidden_layer: which layer of the base neural network to intercept (can be int index or str name)
        online_encoder: encoder for later inference
        online_predictor: MLP to convert a projection into prediction
        target_encoder: encoder to compare, usually EWMA of online encoder
        use_momentum: whether target_encode gets EMA updates from online encoder
        loss_fn: loss function
        moving_average_decay: decay parameter for target encoder
    """

    def __init__(
        self,
        network: nn.Module,
        representation_size: int,
        hidden_layer: Union[int, str] = -2,
        augmentation_function: Optional[
            Callable[[torch.Tensor], Union[torch.Tensor, tuple[torch.Tensor, ...]]]
        ] = None,
        normalization_function: Optional[Callable[[torch.Tensor], torch.Tensor]] = None,
        use_momentum: bool = True,
        projection_size: int = 256,
        projection_hidden_size: int = 1024,
        loss_fn: Callable[[torch.Tensor, torch.Tensor], torch.Tensor] = cosine_loss,
        moving_average_decay: float = 0.99,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__()

        # Set a default augmentation function
        DEFAULT_AUGMENTATION_FUNCTION = nn.Sequential(
            transforms.RandomGrayscale(p=0.2),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(degrees=(0, 360)),
        )
        # Override default augmentation function if given
        self.augmentation_function = (
            augmentation_function
            if augmentation_function is not None
            else DEFAULT_AUGMENTATION_FUNCTION
        )
        self.normalization_function = normalization_function

        self.hidden_layer = hidden_layer

        self.online_encoder = NetWrapper(
            network,
            representation_size,
            layer=hidden_layer,
            projection_size=projection_size,
            projection_hidden_size=projection_hidden_size,
        )
        self.online_predictor = MultiLayerPerceptron(
            projection_size, projection_hidden_size, projection_size
        )
        # Target encoder is initially identical to online encoder
        self.target_encoder = deepcopy(self.online_encoder)

        for parameter in self.target_encoder.parameters():
            parameter.requires_grad = False

        self.use_momentum = use_momentum
        self.loss_fn = loss_fn
        self.moving_average_decay = moving_average_decay

    def forward(
        self,
        x: torch.Tensor,
        return_errors: bool = False,
    ) -> torch.Tensor:
        if not return_errors:
            if self.normalization_function is not None:
                x = self.normalization_function(x)
            encoder_result: torch.Tensor = self.online_encoder(
                x, return_projection=False
            )
            return encoder_result

        # augment_function is stochastic --> image_1 != image_2
        aug_result_1 = self.augmentation_function(x)
        aug_result_2 = self.augmentation_function(x)

        # Handle potential tuple return from augmentation
        image_1 = aug_result_1[0] if isinstance(aug_result_1, tuple) else aug_result_1
        image_2 = aug_result_2[0] if isinstance(aug_result_2, tuple) else aug_result_2

        if self.normalization_function is not None:
            image_1 = self.normalization_function(image_1)
            image_2 = self.normalization_function(image_2)

        online_projection, online_embedding = self.online_encoder(image_1)
        online_prediction = self.online_predictor(online_projection)

        # Only keep track of gradients in online encoder/predictor
        with torch.no_grad():
            target_encoder = (
                self.target_encoder if self.use_momentum else self.online_encoder
            )

            target_projection, target_embedding = target_encoder(image_2)
            target_projection = target_projection.detach()

        loss: torch.Tensor = self.loss_fn(online_prediction, target_projection.detach())
        mean_loss: torch.Tensor = loss.mean()
        return mean_loss

    def update_ma_single_param(
        self, old_value: torch.Tensor, new_value: torch.Tensor
    ) -> torch.Tensor:
        """Get value for a moving average, based on previous and new value.

        Args:
            old_value: previous EMA value
            new_value: new actual value

        Returns:
            Updated EMA value
        """
        return (
            self.moving_average_decay * old_value
            + (1 - self.moving_average_decay) * new_value
        )

    def update_moving_average(self) -> None:
        """Update target encoder with moving average of all parameters."""
        if not self.use_momentum:
            logger.warning("Not updating moving average, use_momentum set to False!")
            return None
        for target_parameters, online_parameters in zip(
            self.target_encoder.parameters(), self.online_encoder.parameters()
        ):
            target_weight, online_weight = (
                target_parameters.data,
                online_parameters.data,
            )
            target_parameters.data = self.update_ma_single_param(
                target_weight, online_weight
            )
