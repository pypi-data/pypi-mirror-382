"""Test assigner for QA class."""

import pandas as pd

from avoca.flags import QA_Flag
from avoca.qa_class.abstract import AbstractQA_Assigner


class TestAssigner(AbstractQA_Assigner):
    """Test assigner for QA class."""

    flag = QA_Flag.MISSING

    def fit(self, data: pd.DataFrame) -> None:
        """Fit the assigner."""
        self.logger.debug("Fitting data with TestAssigner")

    def assign(self, data: pd.DataFrame) -> dict[str, pd.Index]:
        """Assign the data."""
        self.logger.debug("Assigning data with TestAssigner")
        return {}
