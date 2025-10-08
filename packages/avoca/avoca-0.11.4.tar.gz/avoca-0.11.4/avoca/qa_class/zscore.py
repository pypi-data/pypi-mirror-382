"""Quality assurance based on statistical methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from avoca.flags import QA_Flag
from avoca.qa_class.abstract import AbstractQA_Assigner
from avoca.requirements import PythonPackageRequirement

if TYPE_CHECKING:

    from avoca.utils.torch_models import MultipleRegressionModel


class ExtremeValues(AbstractQA_Assigner):
    """Detect extreme values.

    The method is based on the z-score, which is calculated as follows:

    .. math::

        z = \\frac{x - \\mu}{\\sigma}

    where :math:`x` is the value, :math:`\\mu` is the mean of the values
    and :math:`\\sigma` is the standard deviation of the values.

    If the z-score is greater than a threshold, the value is flagged.

    :param variable: The variable to check for extreme values.
    :param threshold: The threshold for the z-score. To flag values.
    :param use_log_normal: If True, the log of the values will be used to calculate the z-score.
        This can be useful if the values are log-normal distributed.
    :param only_greater: If True, only values greater than the threshold will be flagged.
        The values lower than the negative threshold will not be flagged.
        By default, this is True if use_log_normal is True, and False otherwise.
    """

    variable: str
    flag = QA_Flag.EXTREME_VALUE
    threshold: float
    only_greater: bool

    def __init__(
        self,
        variable: str = "",
        threshold: float = 4.0,
        use_log_normal: bool = False,
        only_greater: bool | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.threshold = threshold
        self.use_log_normal = use_log_normal
        if only_greater is None:
            only_greater = True if use_log_normal else False
        self.only_greater = only_greater

        if not variable:
            raise ValueError(f"'variable' must be set for '{self}'")
        self.variable = variable

    @property
    def _stats_columns(self) -> list[tuple[str, str]]:
        """Columns on which the statistics will be calculated."""
        # Get only the columns with the compound and variable
        return [(compound, self.variable) for compound in self.compounds]

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the data by removing infinite values and NaNs."""
        # Clean the infinite values
        df = df.where(np.isfinite(df), np.nan)
        return df

    def fit(self, df: pd.DataFrame):

        self.check_columns_or_raise(df, columns=self._stats_columns)

        self.df_train = df[self._stats_columns]

        if self.use_log_normal:
            # Replace <=0 with NaN
            self.df_train = self.df_train.where(self.df_train > 0, np.nan)
            df = self.df_train.map(lambda x: np.log(x))
        else:
            df = self.df_train

        df = self._clean_data(df)

        self.means = df.mean()
        self.stds = df.std()

    def assign(self, df: pd.DataFrame) -> dict[str, pd.Index]:
        df_zscore = df[self._stats_columns]
        df_zscore = self._clean_data(df_zscore)
        if self.use_log_normal:
            # Replace <=0 with NaN
            df_zscore = df_zscore.where(df_zscore > 0, np.nan)
            df_zscore = df_zscore.map(lambda x: np.log(x))

        self.logger.debug(f"{self.means=}, {self.stds=}")
        df_zscore = (df_zscore - self.means) / self.stds

        self.logger.debug(f"Z-score in assign:\n{df_zscore}")
        self.logger.debug(f"{self.threshold=}")

        df_fail = df_zscore > self.threshold
        if not self.only_greater:
            df_fail = df_fail | (df_zscore < -self.threshold)

        out_dict = {}
        for compound in self.compounds:
            col = (compound, self.variable)
            this_c_fail = df_fail[col]
            out_dict[compound] = this_c_fail.loc[this_c_fail].index

        return out_dict

    def plot(self):

        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(
            len(self.compounds), 1, figsize=(6, 3 * len(self.compounds)), sharex=True
        )

        x = self.dt if hasattr(self, "dt") else self.df_train.index
        x = pd.Series(x, index=self.df_train.index)

        outliers = self.assign(self.df_train)

        for i, compound in enumerate(self.compounds):
            ax = axes[i]
            col = (compound, self.variable)
            ax.scatter(
                x,
                self.df_train[col],
                s=1,
                label="darkblue",
            )
            mean = self.means[col]
            std = self.stds[col]
            top, bottom = mean + std * self.threshold, mean - std * self.threshold
            if self.use_log_normal:
                mean = np.exp(mean)
                top, bottom = np.exp(top), np.exp(bottom)

            ax.axhline(mean, color="C1", label="Mean")
            ax.axhline(top, color="C2", label="Mean + std")
            ax.axhline(bottom, color="C2", label="Mean - std")

            outlier_indices = outliers[compound]
            ax.scatter(
                x.loc[outlier_indices],
                self.df_train.loc[outlier_indices, col],
                s=10,
                marker="x",
                color="red",
                label="Extreme values",
            )
            ax.set_title(
                f"{compound} +- {self.threshold} std",
                # Under teh top line
                y=0.8,
            )
            ax.tick_params(axis="x", rotation=25)

        return fig, axes


class XY_Correlations(AbstractQA_Assigner):
    """Compare values of various compunds using a correlation.

    This assumes the data between two compounds is linearly correlated.
    If a value is outside the threshold around the linear regression line, it is flagged.

    :param variable: The variable to compare the compounds on.
    :param threshold: The threshold for the residuals of the linear regression.
    """

    flag = QA_Flag.UNCORRELATED
    runtypes = ["air"]
    threshold: float
    variable: str

    def __init__(self, threshold: float = 4.0, variable: str = "", **kwargs):
        super().__init__(**kwargs)
        self.threshold = threshold

        if len(self.compounds) < 2:
            raise ValueError(f"At least two compounds are required for {self}.")

        if not variable:
            raise ValueError("variable must be set")
        self.variable = variable

    def fit(self, df: pd.DataFrame):
        self._regressions = {}
        self._stds = {}
        for i, compoundX in enumerate(self.compounds):
            concX = df[(compoundX, self.variable)]
            for j, compoundY in enumerate(self.compounds):
                if compoundX == compoundY:
                    continue
                concY = df[(compoundY, self.variable)]

                mask_valid = np.isfinite(concX) & np.isfinite(concY)
                if mask_valid.sum() < 3:
                    self.logger.warning(
                        f"Cannot compare {compoundY} to {compoundX} because there are"
                        " not enough valid values.\n"
                        f"{self.name} needs at least 3 valid values to train the model."
                    )
                    continue

                # Linear regression
                slope, intercept = np.polyfit(concX[mask_valid], concY[mask_valid], 1)
                self._regressions[(compoundX, compoundY)] = (slope, intercept)

                # Standard deviations and means
                std = np.std(concY - slope * concX - intercept)
                self._stds[(compoundX, compoundY)] = std

        self.df_train = df

    def assign(self, df: pd.DataFrame) -> dict[str, pd.Index]:
        out_dict = {}
        for i, compoundX in enumerate(self.compounds):
            concX = df[(compoundX, self.variable)]
            for j, compoundY in enumerate(self.compounds):
                if compoundY not in out_dict:
                    # Add an empty index
                    out_dict[compoundY] = pd.Index([], dtype=df.index.dtype)
                if compoundX == compoundY:
                    continue
                if (compoundX, compoundY) not in self._regressions:
                    self.logger.error(
                        f"Cannot assign flag based on  {compoundY} to"
                        f" {compoundX} because model could not be trained."
                    )
                    continue
                concY = df[(compoundY, self.variable)]
                slope, intercept = self._regressions[(compoundX, compoundY)]
                std = self._stds[(compoundX, compoundY)]
                # Linear regression
                residuals = concY - slope * concX - intercept
                mask = np.abs(residuals) > self.threshold * std
                if any(mask):
                    index = df.loc[mask].index
                    out_dict[compoundY] = out_dict[compoundY].union(index)

        return out_dict

    def plot(self):

        import matplotlib.pyplot as plt

        n = len(self.compounds)
        fig, axes = plt.subplots(
            n,
            n,
            figsize=(4 * n, 4 * n),
            dpi=n * 30,
        )
        for i, compoundX in enumerate(self.compounds):
            concX = self.df_train[(compoundX, self.variable)]
            for j, compoundY in enumerate(self.compounds):
                if compoundX == compoundY:
                    continue
                if (compoundX, compoundY) not in self._regressions:
                    continue
                concY = self.df_train[(compoundY, self.variable)]
                slope, intercept = self._regressions[(compoundX, compoundY)]
                ax = axes[i, j]
                ax.scatter(concX, concY, s=1, color="darkblue")
                ax.plot(concX, slope * concX + intercept, color="C1")
                mask_bad = (
                    np.abs(concY - slope * concX - intercept)
                    > self.threshold * self._stds[(compoundX, compoundY)]
                )
                ax.scatter(
                    concX[mask_bad], concY[mask_bad], s=10, color="red", marker="x"
                )
                ax.set_title(
                    f"{compoundY} = {slope:.2f} * {compoundX} + {intercept:.2f}",
                    y=0.8,
                    fontsize=6,
                )
                ax.set_xlabel(compoundX)
                ax.set_ylabel(compoundY)


class Multiple_XY_Correlations(XY_Correlations):
    """Compare compounds concentrations with each other.

    Makes multiple linear regression from the compound x to y.
    If a measurement is outside the threshold, it is flagged.

    This can be useful for compounds with different correlated sources.

    .. warning:: This method is not very stable as the linear regression
        fitting is not convex. It is recommended to check what the model is
        doing before using it.
    """

    threshold: float = 4.0

    required_packages = [PythonPackageRequirement.PYTORCH]

    number_of_regression: int

    _models: dict[tuple[str, str], MultipleRegressionModel]

    def __init__(
        self,
        number_of_regression: int = 2,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.logger.warning(
            f"{self} is currently experimental and may not work as expected."
        )
        if number_of_regression < 2:
            raise ValueError("number_of_regression must be >= 2")
        self.number_of_regression = number_of_regression

    def _train_model(self, x, y):
        """Train a pytorch model"""
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
        import torch.optim as optim

        from avoca.utils.torch_models import MultipleRegressionModel

        data = torch.tensor(
            np.concatenate([x.reshape(-1, 1), y.reshape(-1, 1)], axis=1),
            dtype=torch.float32,
        )

        # Create the model
        model = MultipleRegressionModel(self.number_of_regression)

        # Train the model
        optimizer = optim.Adam(model.parameters(), lr=0.01)
        criterion = nn.MSELoss()

        # While the loss is not decreasing, train the model
        max_epochs = 10000
        last_loss = np.inf
        loss = 0
        # Weight more extreme values
        weights = torch.tensor(x * y, dtype=torch.float32, requires_grad=False)
        while last_loss > loss and max_epochs > 0:
            for i in range(100):
                optimizer.zero_grad()
                y_pred = model(data)
                loss = criterion(y_pred * weights, torch.zeros_like(y_pred))
                loss.backward()
                optimizer.step()
                max_epochs -= 1
            last_loss = loss

        return model

    def fit(self, df: pd.DataFrame):
        self._models: dict[tuple[str, str], MultipleRegressionModel] = {}
        self._slopes = {}
        self._stds = {}

        for i, compoundX in enumerate(self.compounds):
            concX = df[(compoundX, self.variable)]
            for j, compoundY in enumerate(self.compounds):
                if compoundX == compoundY:
                    continue
                concY = df[(compoundY, self.variable)]

                mask_not_nan = ~(np.isnan(concX) | np.isnan(concY))
                if mask_not_nan.sum() < 2:
                    self.logger.warning(
                        f"Cannot compare {compoundY} to {compoundX} because there are"
                        " not enough valid values."
                    )
                    continue

                concX = concX[mask_not_nan]
                concY = concY[mask_not_nan]

                # Linear regression
                model = self._train_model(concX.to_numpy(), concY.to_numpy())

                slopes = [linear.weight.item() for linear in model.linears]
                # Linear regression
                residuals = np.power(
                    np.c_[[concY - slope * concX for slope in slopes]],
                    2,
                )
                # Now we need to calculate of each model the standard deviation
                indexes_regression = np.apply_along_axis(np.argmin, 0, residuals)
                # Make the mean of the residuals for each model and get the standard deviation from each model
                stds = np.sqrt(
                    [
                        np.mean(residuals[i, indexes_regression == i])
                        for i in range(self.number_of_regression)
                    ]
                )
                # Save the model and the standard deviation
                self._models[(compoundX, compoundY)] = model
                self._slopes[(compoundX, compoundY)] = slopes
                self._stds[(compoundX, compoundY)] = stds

    def assign(self, df: pd.DataFrame) -> dict[str, pd.Index]:

        out_dict = {}

        for i, compoundX in enumerate(self.compounds):
            concX = df[(compoundX, self.variable)]
            for j, compoundY in enumerate(self.compounds):
                if compoundX == compoundY:
                    continue
                if (compoundX, compoundY) not in self._models:
                    self.logger.error(
                        f"Cannot assign flag based on  {compoundY} to"
                        f" {compoundX} because model could not be trained."
                    )
                    continue
                concY = df[(compoundY, self.variable)]

                residuals = np.abs(
                    np.c_[
                        [
                            concY - slope * concX
                            for slope in self._slopes[(compoundX, compoundY)]
                        ]
                    ]
                )
                # Now we need to calculate of each model the standard deviation
                indexes_regression = np.apply_along_axis(np.argmin, 0, residuals)
                best_residuals = residuals[
                    indexes_regression,
                    np.arange(len(indexes_regression)),
                ]
                mask = (
                    best_residuals
                    > self.threshold
                    * self._stds[(compoundX, compoundY)][indexes_regression]
                )
                if any(mask):
                    index = df.loc[mask].index
                    if compoundY not in out_dict:
                        out_dict[compoundY] = index
                    else:
                        out_dict[compoundY] = out_dict[compoundY].union(index)

        return out_dict

    def plot(self):
        raise NotImplementedError()
