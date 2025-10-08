from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from avoca.flags import QA_Flag
from avoca.qa_class.abstract import AbstractQA_Assigner

logger = logging.getLogger(__name__)


class InvalidValues(AbstractQA_Assigner):
    """Flag invalid values.

    :param variables:
        The variables to be flagged. If a string is given, it will be converted to a list.
    :para m flag:
        The flag to be assigned. Default is :py:attr:`QA_Flag.INVALID_VALUES`.
    :param negative_values:
        If True, negative values will be flagged. Default is False.
    :param zeroes:
        If True, zero values will be flagged. Default is False.
    """

    flag: QA_Flag = QA_Flag.INVALID_VALUES
    negative_values: bool
    zeroes: bool

    def __init__(
        self,
        variable: str,
        negative_values: bool = False,
        zeroes: bool = False,
        **kwargs,
    ):
        """Create a new InvalidValues assigner."""

        super().__init__(**kwargs)

        self.variable = variable

        self.negative_values = negative_values
        self.zeroes = zeroes

        self._columns = [(compound, self.variable) for compound in self.compounds]

    def fit(self, df: pd.DataFrame):
        """Fit the assigner to the data.

        :param df:
            The data to be fitted.
        """
        # Check that the columns are in the dataframe
        self.check_columns_or_raise(df, self._columns)

    def _flagged_indices(self, series: pd.Series) -> pd.Index:
        """Flag the invalid values in the series.

        :param series:
            The series to be flagged.
        """
        # Check that the series is a float
        if not pd.api.types.is_float_dtype(series):
            raise ValueError(f"{series.name} is not a float series.")

        # Create a mask for the invalid values
        mask = ~np.isfinite(series)

        if self.negative_values:
            mask |= series < 0.0
        if self.zeroes:
            mask |= series == 0.0

        # Flag the invalid values
        return series.index[mask]

    def assign(self, df: pd.DataFrame) -> dict[str, pd.Index]:
        """Assign the flag to the invalid values.

        :param df:
            The data to be flagged.
        """
        # Check that the columns are in the dataframe
        self.check_columns_or_raise(df, self._columns)

        # Check that the flag is a QA_Flag
        return {
            cmp: self._flagged_indices(df[(cmp, self.variable)])
            for cmp in self.compounds
        }
