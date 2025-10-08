"""Quality assurance for retention times."""

from __future__ import annotations

import numpy as np
import pandas as pd

from avoca.flags import QA_Flag
from avoca.logging import SUSPISCIOUS
from avoca.qa_class.abstract import AbstractQA_Assigner


class RetentionTimeChecker(AbstractQA_Assigner):
    """Tries to check if there is a problem with the assignment of the retention times.

    The very simple way of doing, it to check the correlation between the
    retention times of the measurements.
    The correlation is usually very high. If one compound has a low correlation
    with the others, it probably means that is was miss-assigned at some points.

    :param rt_threshold: The threshold for the retention time deviation.
        Unit is time unit (minutes or seconds, as in the data).
        This will try to fit a linear regression from the average training
        retention times to the measured ones for each sample.
        If after the regression a datapoint is higher than this threshold,
        it will be removed.
    :param rt_relative_max_deviation: The maximum relative deviation allowed
        from the average retention time.
        This is used to remove outliers that are too far from the average.
        if 0.5 is given, it means that the retention time can be 50% higher or lower
        than the average retention time.
    """

    runtypes: list[str] = ["air", "std"]
    variable: str = "rt"
    flag = QA_Flag.SUSPICIOUS_RT

    rt_ref: pd.Series

    def __init__(
        self,
        rt_threshold: float = 2.0,
        rt_relative_max_deviation: float = 0.2,
        poly_order: int = 1,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.rt_threshold = rt_threshold
        self.rt_relative_max_deviation = rt_relative_max_deviation
        self.poly_order = poly_order

    def fit(self, df: pd.DataFrame):
        cols = [(compound, "rt") for compound in self.compounds]

        df_rt: pd.DataFrame = df[cols]
        self.df_train = df_rt
        df_corr = df_rt.corr()
        self.corr = df_corr.mean()
        mean_corr = self.corr.mean()
        std_corr = self.corr.std()

        deviation = np.abs(self.corr - mean_corr)
        threshold = 2 * std_corr
        self.logger.debug(f"{deviation=}, {threshold=}")

        possibly_wrong = deviation > threshold
        self.possibly_wrong = possibly_wrong[possibly_wrong].index.tolist()
        if len(self.possibly_wrong) > 0:
            self.logger.log(
                SUSPISCIOUS, f"Possibe RT assignement issue: {self.possibly_wrong=}"
            )

        # Get a dataframe for a mean reference
        self.rt_ref = df_rt.median(axis="index")
        self.rt_std = df_rt.std(axis="index")

    def assign(self, df: pd.DataFrame) -> dict[str, pd.Index]:
        """Assing flags when expected rt values does not match the measured ones."""
        rt_cols: list[tuple[str, str]] = [
            (compound, "rt") for compound in self.compounds
        ]
        df_rt = df[rt_cols]
        # Take the reference retention times
        x = self.rt_ref.loc[rt_cols].to_numpy()
        std = self.rt_std.loc[rt_cols].to_numpy()

        outliers = {}

        for t, row in df_rt.iterrows():
            # Make a lin reg line
            y = row.to_numpy()
            # Remove the points that are too far from the reference
            mask_bad = (
                (np.abs(y - x) / x) > self.rt_relative_max_deviation
            ) | np.isnan(y)

            if np.sum(~mask_bad) > self.poly_order + 2:

                params = np.polyfit(x[~mask_bad], y[~mask_bad], self.poly_order)
                f = np.poly1d(params)
                y_lin_reg = f(x)

                # Get the points which are too far from the reg line
                error = y - y_lin_reg
                mask_bad |= np.abs(error) > self.rt_threshold

            if any(mask_bad):
                outliers[t] = mask_bad

        # Create a dataframe with the flags
        out_dict = {}
        df_outliers = pd.DataFrame(outliers, index=self.compounds).T

        for compound in self.compounds:
            col = df_outliers[compound]
            out_dict[compound] = col.loc[col].index

        return out_dict

    def plot(self):

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(16, 9))

        assigned = self.assign(self.df_train)

        for compound in self.compounds:
            points = ax.scatter(
                self.df_train.index,
                self.df_train[(compound, "rt")],
                label=compound,
                marker="+",
            )
            df_flagged = self.df_train.loc[assigned[compound]]
            if len(df_flagged) > 0:
                ax.scatter(
                    df_flagged.index,
                    df_flagged[(compound, "rt")],
                    # label=f"{compound} flagged",
                    color="red",
                    marker="x",
                )
            # Line for the mean retention time
            ax.axhline(
                self.rt_ref[(compound, "rt")],
                color=points.get_facecolor()[0],
                linestyle="--",
            )

        ax.set_ylabel("Retention time")
        ax.set_xlabel("Sample")

        ax.legend()
        plt.show()
