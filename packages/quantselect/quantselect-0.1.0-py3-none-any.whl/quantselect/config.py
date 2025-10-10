"""
Configuration module for QuantSelect.

This module provides a comprehensive configuration system for the QuantSelect package,
including model parameters, training parameters, and validation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field, asdict
import torch.nn as nn
import torch.optim as optim


@dataclass
class CriterionConfig:
    """Configuration for loss function parameters."""

    alpha: float = 0.8
    epsilon: float = 1e-8
    kind: str = "WVL"
    lambda1: float = 0.0

    def __post_init__(self):
        """Validate criterion parameters after initialization."""
        if not 0.0 <= self.alpha <= 1.0:
            raise ValueError(f"alpha must be between 0.0 and 1.0, got {self.alpha}")
        if self.epsilon <= 0:
            raise ValueError(f"epsilon must be positive, got {self.epsilon}")
        if self.kind not in ["WVL", "MSE", "MAE"]:
            raise ValueError(
                f"kind must be one of ['WVL', 'MSE', 'MAE'], got {self.kind}"
            )
        if self.lambda1 < 0:
            raise ValueError(f"lambda1 must be non-negative, got {self.lambda1}")


@dataclass
class ModelConfig:
    """Configuration for neural network model parameters."""

    hidden_sizes: Union[int, List[int]] = 4
    dropout_rate: Optional[float] = None
    activation: nn.Module = field(default_factory=nn.ReLU)
    init: str = "uniform"
    batch_norm: bool = True
    normalize: bool = False
    output_activation: str = "sigmoid"

    def __post_init__(self):
        """Validate model parameters after initialization."""
        if isinstance(self.hidden_sizes, int) and self.hidden_sizes <= 0:
            raise ValueError(f"hidden_sizes must be positive, got {self.hidden_sizes}")
        if isinstance(self.hidden_sizes, list) and not all(
            h > 0 for h in self.hidden_sizes
        ):
            raise ValueError(
                f"All hidden_sizes must be positive, got {self.hidden_sizes}"
            )

        if self.dropout_rate is not None and not 0.0 <= self.dropout_rate <= 1.0:
            raise ValueError(
                f"dropout_rate must be between 0.0 and 1.0, got {self.dropout_rate}"
            )

        if self.init not in ["uniform", "zero", "xavier", "kaiming"]:
            raise ValueError(
                f"init must be one of ['uniform', 'zero', 'xavier', 'kaiming'], got {self.init}"
            )

        if self.output_activation not in ["sigmoid", "tanh", "relu", "linear"]:
            raise ValueError(
                f"output_activation must be one of ['sigmoid', 'tanh', 'relu', 'linear'], got {self.output_activation}"
            )


@dataclass
class OptimizerConfig:
    """Configuration for optimizer parameters."""

    lr: float = 1e-2
    weight_decay: float = 0.0
    betas: tuple = (0.9, 0.999)
    eps: float = 1e-8
    optimizer_type: str = "Adam"

    def __post_init__(self):
        """Validate optimizer parameters after initialization."""
        if self.lr <= 0:
            raise ValueError(f"learning rate must be positive, got {self.lr}")
        if self.weight_decay < 0:
            raise ValueError(
                f"weight_decay must be non-negative, got {self.weight_decay}"
            )
        if not all(0 < beta < 1 for beta in self.betas):
            raise ValueError(f"betas must be between 0 and 1, got {self.betas}")
        if self.eps <= 0:
            raise ValueError(f"eps must be positive, got {self.eps}")
        if self.optimizer_type not in ["Adam", "SGD", "AdamW", "RMSprop"]:
            raise ValueError(
                f"optimizer_type must be one of ['Adam', 'SGD', 'AdamW', 'RMSprop'], got {self.optimizer_type}"
            )


@dataclass
class FitConfig:
    """Configuration for training parameters."""

    epochs: int = 40
    batch_size: int = 64
    shuffle: bool = False
    train_size: int = 200
    verbose: bool = True
    validation_split: float = 0.2
    early_stopping_patience: Optional[int] = None
    learning_rate_scheduler: Optional[str] = None
    save_best_model: bool = False
    model_save_path: Optional[str] = None

    def __post_init__(self):
        """Validate training parameters after initialization."""
        if self.epochs <= 0:
            raise ValueError(f"epochs must be positive, got {self.epochs}")
        if self.batch_size <= 0:
            raise ValueError(f"batch_size must be positive, got {self.batch_size}")
        if self.train_size <= 0:
            raise ValueError(f"train_size must be positive, got {self.train_size}")
        if not 0.0 < self.validation_split < 1.0:
            raise ValueError(
                f"validation_split must be between 0.0 and 1.0, got {self.validation_split}"
            )
        if (
            self.early_stopping_patience is not None
            and self.early_stopping_patience <= 0
        ):
            raise ValueError(
                f"early_stopping_patience must be positive, got {self.early_stopping_patience}"
            )
        if (
            self.learning_rate_scheduler is not None
            and self.learning_rate_scheduler
            not in ["StepLR", "ReduceLROnPlateau", "CosineAnnealingLR"]
        ):
            raise ValueError(
                f"learning_rate_scheduler must be one of ['StepLR', 'ReduceLROnPlateau', 'CosineAnnealingLR'], got {self.learning_rate_scheduler}"
            )


@dataclass
class PlotConfig:
    """Configuration for matplotlib and seaborn plot styling."""

    # Font sizes
    small_size: int = 8
    medium_size: int = 8

    # Font settings
    font_family: str = "Arial"

    # Colors
    text_color: str = "#4E4F51"

    # Figure settings
    figure_dpi: int = 150
    pdf_fonttype: int = 42

    # Background colors
    axes_facecolor: str = "white"
    figure_facecolor: str = "white"

    # Line settings
    line_width: float = 1.0
    axes_linewidth: float = 0.6
    xtick_major_width: float = 0.6
    ytick_major_width: float = 0.6

    # Seaborn settings
    seaborn_style: str = "ticks"
    seaborn_context: str = "paper"

    def __post_init__(self):
        """Validate plot configuration parameters."""
        if self.small_size <= 0:
            raise ValueError(f"small_size must be positive, got {self.small_size}")
        if self.medium_size <= 0:
            raise ValueError(f"medium_size must be positive, got {self.medium_size}")
        if self.figure_dpi <= 0:
            raise ValueError(f"figure_dpi must be positive, got {self.figure_dpi}")
        if self.line_width <= 0:
            raise ValueError(f"line_width must be positive, got {self.line_width}")
        if self.axes_linewidth <= 0:
            raise ValueError(
                f"axes_linewidth must be positive, got {self.axes_linewidth}"
            )
        if self.seaborn_style not in [
            "darkgrid",
            "whitegrid",
            "dark",
            "white",
            "ticks",
        ]:
            raise ValueError(
                f"seaborn_style must be one of ['darkgrid', 'whitegrid', 'dark', 'white', 'ticks'], got {self.seaborn_style}"
            )
        if self.seaborn_context not in ["paper", "notebook", "talk", "poster"]:
            raise ValueError(
                f"seaborn_context must be one of ['paper', 'notebook', 'talk', 'poster'], got {self.seaborn_context}"
            )

    def get_matplotlib_rcparams(self) -> Dict[str, Any]:
        """
        Get matplotlib RC parameters dictionary.

        Returns
        -------
        Dict[str, Any]
            Dictionary of matplotlib RC parameters
        """
        return {
            "font.size": self.small_size,
            "font.family": self.font_family,
            "axes.titlesize": self.medium_size,
            "axes.labelsize": self.medium_size,
            "xtick.labelsize": self.small_size,
            "ytick.labelsize": self.small_size,
            "legend.fontsize": self.small_size,
            "figure.titlesize": self.medium_size,
            "figure.dpi": self.figure_dpi,
            "text.color": self.text_color,
            "axes.labelcolor": self.text_color,
            "axes.edgecolor": self.text_color,
            "xtick.color": self.text_color,
            "ytick.color": self.text_color,
            "lines.linewidth": self.line_width,
            "axes.linewidth": self.axes_linewidth,
            "xtick.major.width": self.xtick_major_width,
            "ytick.major.width": self.ytick_major_width,
            "pdf.fonttype": self.pdf_fonttype,
            "axes.facecolor": self.axes_facecolor,
            "figure.facecolor": self.figure_facecolor,
        }


class QuantSelectConfig:
    """
    Main configuration class for QuantSelect.

    This class provides a centralized configuration system with validation,
    serialization, and easy parameter management.
    """

    def __init__(
        self,
        criterion_config: Optional[CriterionConfig] = None,
        model_config: Optional[ModelConfig] = None,
        optimizer_config: Optional[OptimizerConfig] = None,
        fit_config: Optional[FitConfig] = None,
        plot_config: Optional[PlotConfig] = None,
    ):
        """
        Initialize QuantSelectConfig with optional custom configurations.

        Parameters
        ----------
        criterion_config : CriterionConfig, optional
            Custom criterion configuration
        model_config : ModelConfig, optional
            Custom model configuration
        optimizer_config : OptimizerConfig, optional
            Custom optimizer configuration
        fit_config : FitConfig, optional
            Custom training configuration
        plot_config : PlotConfig, optional
            Custom plot styling configuration
        """
        self.criterion_config = criterion_config or CriterionConfig()
        self.model_config = model_config or ModelConfig()
        self.optimizer_config = optimizer_config or OptimizerConfig()
        self.fit_config = fit_config or FitConfig()
        self.plot_config = plot_config or PlotConfig()

    @property
    def CONFIG(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the configuration as a dictionary for backward compatibility.

        Returns
        -------
        Dict[str, Dict[str, Any]]
            Configuration dictionary with the same structure as the original ModelConfig.CONFIG
        """
        return {
            "criterion_params": asdict(self.criterion_config),
            "model_params": asdict(self.model_config),
            "optmizer_params": asdict(self.optimizer_config),
            "fit_params": asdict(self.fit_config),
            "plot_params": asdict(self.plot_config),
        }

    def update(self, config_dict: Dict[str, Dict[str, Any]]) -> None:
        """
        Update configuration from a dictionary.

        Parameters
        ----------
        config_dict : Dict[str, Dict[str, Any]]
            Dictionary containing configuration updates
        """
        if "criterion_params" in config_dict:
            for key, value in config_dict["criterion_params"].items():
                if hasattr(self.criterion_config, key):
                    setattr(self.criterion_config, key, value)

        if "model_params" in config_dict:
            for key, value in config_dict["model_params"].items():
                if hasattr(self.model_config, key):
                    setattr(self.model_config, key, value)

        if "optmizer_params" in config_dict:
            for key, value in config_dict["optmizer_params"].items():
                if hasattr(self.optimizer_config, key):
                    setattr(self.optimizer_config, key, value)

        if "fit_params" in config_dict:
            for key, value in config_dict["fit_params"].items():
                if hasattr(self.fit_config, key):
                    setattr(self.fit_config, key, value)

        if "plot_params" in config_dict:
            for key, value in config_dict["plot_params"].items():
                if hasattr(self.plot_config, key):
                    setattr(self.plot_config, key, value)

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Convert configuration to dictionary.

        Returns
        -------
        Dict[str, Dict[str, Any]]
            Configuration as dictionary
        """
        return self.CONFIG

    def to_json(self, filepath: Optional[Union[str, Path]] = None) -> str:
        """
        Convert configuration to JSON string or save to file.

        Parameters
        ----------
        filepath : str or Path, optional
            Path to save JSON file. If None, returns JSON string.

        Returns
        -------
        str
            JSON string if filepath is None, otherwise empty string
        """
        config_dict = self.to_dict()

        # Convert torch.nn.Module to string representation
        if isinstance(config_dict["model_params"]["activation"], nn.Module):
            config_dict["model_params"]["activation"] = str(
                config_dict["model_params"]["activation"]
            )

        json_str = json.dumps(config_dict, indent=2, default=str)

        if filepath is not None:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)
            return ""

        return json_str

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Dict[str, Any]]) -> "QuantSelectConfig":
        """
        Create configuration from dictionary.

        Parameters
        ----------
        config_dict : Dict[str, Dict[str, Any]]
            Configuration dictionary

        Returns
        -------
        QuantSelectConfig
            Configuration instance
        """
        criterion_config = CriterionConfig(**config_dict.get("criterion_params", {}))
        model_config = ModelConfig(**config_dict.get("model_params", {}))
        optimizer_config = OptimizerConfig(**config_dict.get("optmizer_params", {}))
        fit_config = FitConfig(**config_dict.get("fit_params", {}))
        plot_config = PlotConfig(**config_dict.get("plot_params", {}))

        return cls(
            criterion_config, model_config, optimizer_config, fit_config, plot_config
        )

    @classmethod
    def from_json(cls, filepath: Union[str, Path]) -> "QuantSelectConfig":
        """
        Create configuration from JSON file.

        Parameters
        ----------
        filepath : str or Path
            Path to JSON configuration file

        Returns
        -------
        QuantSelectConfig
            Configuration instance
        """
        with open(filepath, "r", encoding="utf-8") as f:
            config_dict = json.load(f)

        return cls.from_dict(config_dict)

    def get_optimizer_class(self):
        """
        Get the optimizer class based on configuration.

        Returns
        -------
        torch.optim.Optimizer
            Optimizer class
        """
        optimizer_map = {
            "Adam": optim.Adam,
            "SGD": optim.SGD,
            "AdamW": optim.AdamW,
            "RMSprop": optim.RMSprop,
        }
        return optimizer_map.get(self.optimizer_config.optimizer_type, optim.Adam)

    def __repr__(self) -> str:
        """String representation of the configuration."""
        return (
            f"QuantSelectConfig(\n"
            f"  criterion_config={self.criterion_config},\n"
            f"  model_config={self.model_config},\n"
            f"  optimizer_config={self.optimizer_config},\n"
            f"  fit_config={self.fit_config},\n"
            f"  plot_config={self.plot_config}\n"
            f")"
        )


def apply_plot_style(plot_config: Optional[PlotConfig] = None) -> None:
    """
    Apply matplotlib and seaborn styling configuration.

    This function sets up consistent plotting styles across the entire project
    by configuring matplotlib RC parameters and seaborn theme.

    Parameters
    ----------
    plot_config : PlotConfig, optional
        Plot configuration object. If None, uses default PlotConfig.

    Examples
    --------
    >>> from quantselect.config import apply_plot_style, PlotConfig
    >>>
    >>> # Use default styling
    >>> apply_plot_style()
    >>>
    >>> # Use custom styling
    >>> custom_config = PlotConfig(small_size=10, medium_size=12)
    >>> apply_plot_style(custom_config)
    >>>
    >>> # Use from QuantSelectConfig
    >>> from quantselect.config import QuantSelectConfig
    >>> config = QuantSelectConfig()
    >>> apply_plot_style(config.plot_config)
    """
    import matplotlib.pyplot as plt
    import seaborn as sns

    if plot_config is None:
        plot_config = PlotConfig()

    # Get matplotlib RC parameters from config
    rc_params = plot_config.get_matplotlib_rcparams()

    # Apply matplotlib styling
    plt.rcParams.update(rc_params)

    # Apply seaborn theme
    sns.set_theme(
        style=plot_config.seaborn_style,
        context=plot_config.seaborn_context,
        rc=rc_params,
    )


def get_default_plot_config() -> PlotConfig:
    """
    Get the default plot configuration.

    Returns
    -------
    PlotConfig
        Default plot configuration object
    """
    return PlotConfig()
