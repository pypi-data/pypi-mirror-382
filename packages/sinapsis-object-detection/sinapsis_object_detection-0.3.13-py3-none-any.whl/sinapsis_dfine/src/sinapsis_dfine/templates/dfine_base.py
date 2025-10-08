# -*- coding: utf-8 -*-
import gc
import os
from abc import abstractmethod
from typing import Literal

import torch
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import (
    OutputTypes,
    TemplateAttributes,
    TemplateAttributeType,
    UIPropertiesMetadata,
)
from sinapsis_core.utils.env_var_keys import SINAPSIS_CACHE_DIR
from sinapsis_generic_data_tools.helpers.file_downloader import download_file

from sinapsis_dfine.helpers.tags import Tags


@dataclass(frozen=True)
class DFINEKeys:
    """Defines constants used as keys in configurations and updates."""

    CONFIG: str = "config"
    RESUME: str = "resume"
    TUNING: str = "tuning"
    SEED: str = "seed"
    USE_AMP: str = "use_amp"
    OUTPUT_DIR: str = "output_dir"
    DEVICE: str = "device"
    HGNET_V2: str = "HGNetv2"


class PretrainedModels(BaseModel):
    """Defines the attributes for a pretrained model."""

    size: Literal["n", "s", "m", "l", "x"] = "n"
    variant: Literal["coco", "obj365", "custom"] = "coco"


class DFINEBaseAttributes(TemplateAttributes):
    """Defines the general attributes required for D-FINE workflows.

    Attributes:
        config_file (str): Path to the model configuration file. It must be provided and follow
            the general structure as defined in the original D-FINE repository.
        pretrained_model (PretrainedModels | None): Specifies the size and variant of the
            pretrained model. If omitted, it defaults to PretrainedModels(size='n', variant='coco').
            Can be explicitly used for custom weights by setting `variant = 'custom'`.
        device (Literal["cpu", "cuda"]): Device to run the model ('cpu' or 'cuda').
        weights_path (str | None): Path to custom weights file, if provided. Defaults to None.
        output_dir (str): Directory for storing outputs and downloaded weights. Defaults to
            SINAPSIS_CACHE_DIR.

    """

    config_file: str
    pretrained_model: PretrainedModels = Field(default_factory=PretrainedModels)
    device: Literal["cpu", "cuda"]
    weights_path: str | None = None
    output_dir: str = str(SINAPSIS_CACHE_DIR)


class DFINEBase(Template):
    """
    Base class for shared logic in D-FINE Training and Inference workflows.

    The template validates that the configuration for the model is correct, and that
    the model has the correct size and weights to perform both inference and training.

    Raises:
        ValueError: If one of the attributes is defined incorrectly or missing for the wanted
            mode.
        FileNotFoundError: If the config file provided does not exist in the provided path.
    """

    AttributesBaseModel = DFINEBaseAttributes
    UIProperties = UIPropertiesMetadata(
        category="D-FINE",
        output_type=OutputTypes.IMAGE,
        tags=[Tags.DFINE, Tags.IMAGE, Tags.INFERENCE, Tags.MODELS, Tags.TRAINING, Tags.OBJECT_DETECTION],
    )
    SUPPORTED_HGNET_BACKBONES = ("B0", "B1", "B2", "B3", "B4", "B5", "B6")
    WEIGHTS_BASE_URL = "https://github.com/Peterande/storage/releases/download/dfinev1.0/"
    KEYS = DFINEKeys()

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        self.initialize()

    def initialize(self) -> None:
        """Initializes the template's common state for creation or reset.

        This method is called by both `__init__` and `reset_state` to ensure
        a consistent state. Can be overriden by subclasses for specific behaviour.
        """
        if not os.path.exists(self.attributes.output_dir):
            os.makedirs(self.attributes.output_dir)
        if not self.attributes.output_dir.endswith("/"):
            self.attributes.output_dir += "/"

    def _validate_config_file(self) -> None:
        """Ensures the configuration file exists.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
        """
        if not os.path.exists(self.attributes.config_file):
            raise FileNotFoundError(f"Config file not found: {self.attributes.config_file}")

    def _validate_pretrained_model(self) -> None:
        """Validates the pretrained model attributes.

        Raises:
            ValueError: If the model variant or size is unsupported.
        """
        if self.attributes.pretrained_model.variant == "custom":
            return

        if self.attributes.pretrained_model.variant == "obj365" and self.attributes.pretrained_model.size == "n":
            raise ValueError("The 'n' model size is not available for 'obj365' pretrained models.")

    def _download_dfine_weights(self) -> str:
        """Downloads D-FINE weights based on the pretrained model configuration.

        Returns:
            str: Path to the downloaded D-FINE weights.
        """
        if self.attributes.pretrained_model.variant == "custom":
            raise RuntimeError("_download_dfine_weights should not be called for 'custom' variant.")

        model_size = self.attributes.pretrained_model.size
        model_variant = self.attributes.pretrained_model.variant

        dfine_weights_filename = f"dfine_{model_size}_{model_variant}.pth"
        dfine_weights_path = os.path.join(self.attributes.output_dir, dfine_weights_filename)
        dfine_weights_url = self.WEIGHTS_BASE_URL + dfine_weights_filename
        download_file(dfine_weights_url, dfine_weights_path, f"D-FINE {model_variant.upper()} weights ({model_size})")

        return dfine_weights_path

    @abstractmethod
    def _cleanup(self) -> None:
        """Subclasses must implement this to delete their specific heavy objects."""

    def reset_state(self, template_name: str | None = None) -> None:
        """Releases the heavy resources from memory and re-instantiates the template.

        Args:
            template_name (str | None, optional): The name of the template instance being reset. Defaults to None.
        """
        _ = template_name

        self._cleanup()

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.initialize()
        self.logger.info(f"Reset template instance `{self.instance_name}`")
