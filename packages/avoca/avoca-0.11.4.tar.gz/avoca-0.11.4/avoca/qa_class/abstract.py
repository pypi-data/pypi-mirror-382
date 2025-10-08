"""Abstract class for QA assigners."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Sequence

import pandas as pd

from avoca.flags import QA_Flag
from avoca.requirements import PythonPackageRequirement

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


class AbstractQA_Assigner(ABC):
    """Abstract class for QA assigners.

    Inheriting from this class will create a QA assigner that can be used to
    assign QA flags to data.

    The principle is that you fit the assigner on some data, and then you can
    use it to assign QA flags to other data.

    The trained data is assumed to be already QA'd, so the QA assigner will
    only learn from the data that is not missing.

    Attributes:

        flags: The QA flags that will be assigned to the data.
        runtypes: The runtypes that the QA assigner should use.

    Future work:

            * Make it possible to quiclky save and load them.
    """

    # Automatic attributes for every QA assigner
    logger: logging.Logger

    # Must be set by the child class
    df_train: pd.DataFrame
    dt: pd.Series  # datetime serie

    # Attributes that depend on the QA assigner
    flag: QA_Flag
    runtypes: list[str] | None
    required_packages: list[PythonPackageRequirement] | None = None

    # Options that can be set by the user
    name: str
    compounds: list[str]
    start: pd.Timestamp
    stopp: pd.Timestamp

    def __new__(cls, *args, **kwargs):
        """Create a new QA assigner."""
        if not hasattr(cls, "flag"):
            raise ValueError(
                f"Class {cls.__name__} does not have the required attribute"
                " flag. \n It cannot be instantiated."
            )
        if not isinstance(cls.flag, QA_Flag):
            raise ValueError(
                f"Class {cls.__name__} has the attribute flags but it is not"
                " a QA_Flag. \n It cannot be instantiated."
            )
        return super().__new__(cls)

    def __init__(
        self,
        *args,
        compounds: list[str] = [],
        start: pd.Timestamp = pd.Timestamp.min,
        stopp: pd.Timestamp = pd.Timestamp.max,
        name: str | None = None,
        runtypes: list[str] = None,
        log_level: int = logging.INFO,
    ):
        """Create a new QA assigner."""
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(log_level)

        self.name = name or type(self).__name__

        if hasattr(self, "runtypes") and runtypes is not None:
            raise ValueError(
                f"{self} has {self.runtypes=}. It cannot accept other runtypes."
            )
        self.runtypes = runtypes

        if args:
            raise ValueError(
                f"{AbstractQA_Assigner} does not take any positional arguments."
            )
        if not compounds:
            raise ValueError(f"{self} must have at least one compound.")
        self.logger.debug(f"Creating {self} with {compounds=}")
        self.compounds = compounds

        # Check the types
        if not isinstance(start, pd.Timestamp):
            raise ValueError(f"{start=} is not a pd.Timestamp.")
        if not isinstance(stopp, pd.Timestamp):
            raise ValueError(f"{stopp=} is not a pd.Timestamp.")
        self.start = start
        self.stopp = stopp

        if self.required_packages is not None:
            for package in self.required_packages:
                if not package.check():
                    raise ImportError(
                        f"The package {package.value} is required for"
                        f" {type(self).__name__}. \nPlease install it and try again or"
                        " use another method."
                    )

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name})"

    def check_columns_or_raise(
        self, df: pd.DataFrame, columns: Sequence[tuple[str, str] | str]
    ) -> None:
        """Check that the columns are in the dataframe or raise an error."""
        missing_columns = [c for c in columns if c not in df.columns]
        if missing_columns:
            raise ValueError(
                f"Assigner {self} requires columns {missing_columns} to be"
                " in the dataframe but they are not. \n "
                f"Please check the data and the settings for {self.name}"
            )

        # Check columns full of nans
        full_nan_columns = df[columns].isna().all(axis="index")
        if full_nan_columns.any():
            self.logger.warning(
                f"Assigner {self} has columns {df[columns].columns[full_nan_columns]}"
                "  full of nans. \n "
                f"Please check the data and the settings for {self.name}"
            )

    @abstractmethod
    def fit(self, df: pd.DataFrame):
        """Fit the QA assigner on some data.

        Args:
            df: The data to train on.
        """
        raise NotImplementedError

    @abstractmethod
    def assign(self, df: pd.DataFrame) -> dict[str, pd.Index]:
        """Assigns QA flags to data.

        Args:
            df: The data to assign QA flags to.

        Returns:
            A dictionary mapping the compounds to the indices of the rows that
            should be flagged.

        """
        raise NotImplementedError

    # Optional method
    def plot(self) -> tuple[Figure, Sequence[Axes]]:
        """Plot the QA assigner."""
        raise NotImplementedError(f"{type(self).__name__} does not have a plot method.")
