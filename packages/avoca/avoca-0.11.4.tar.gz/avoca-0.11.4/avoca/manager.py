"""Factory function for creating Assigner of the correct type."""

from __future__ import annotations

import logging

import pandas as pd

from avoca.flagging import flag
from avoca.qa_class.abstract import AbstractQA_Assigner
from avoca.settings import AssignerSettings
from avoca.utils import compounds_from_df, runtypes_from_df

logger = logging.getLogger(__name__)


class AssignerManager:
    """Factory function for creating Assigner of the correct type."""

    _assigners_importpath = {
        "RetentionTimeChecker": "avoca.qa_class.rt",
        "ExtremeValues": "avoca.qa_class.zscore",
        "ExtremeConcentrations": "avoca.qa_class.concs",
        "XY_Correlations": "avoca.qa_class.zscore",
        "TestAssigner": "avoca.qa_class.test",
        "InvalidValues": "avoca.qa_class.invalid",
    }

    # A bunch of variables that should not be passed to the assigner
    _init_vars = {
        # define which assigner to use
        "model",
        # Key word arguments that are passed to the assigner
        "params",
    }

    @staticmethod
    def create(
        settings: AssignerSettings, default_compounds: list[str] = []
    ) -> AbstractQA_Assigner:
        """Create a QA assigner from a setting.

        Args:
            settings: The settings to use to create the assigner.

        Returns:
            A QA assigner.
        """

        assigner_class_str = settings.model

        if assigner_class_str not in AssignerManager._assigners_importpath:
            raise ValueError(
                f"Unknown assigner type '{assigner_class_str}'.  \n Available are:"
                f" {', '.join(AssignerManager._assigners_importpath.keys())}"
            )

        # Import the assigner class from the correct module
        assigner_importpath = AssignerManager._assigners_importpath[assigner_class_str]
        assigner_module = __import__(assigner_importpath, fromlist=[""])
        assigner_class = getattr(assigner_module, assigner_class_str)

        # Parse the settings
        logger.info(
            f"Creating assigner {assigner_class_str} with settings:"
            f" {settings.model_dump()}"
        )

        if "compounds" not in settings.params:
            # Set the default compounds if not specified
            settings.params["compounds"] = default_compounds

        return assigner_class(
            **{
                key: item
                for key, item in settings.model_dump().items()
                if key not in AssignerManager._init_vars
            }
            | settings.params
        )

    @staticmethod
    def train(assigner: AbstractQA_Assigner, df: pd.DataFrame):
        # Check that the compounds are okay
        compounds_of_df = compounds_from_df(df)
        if not assigner.compounds:
            # Set all the compounds if not specified
            assigner.compounds = compounds_of_df
        if not set(assigner.compounds).issubset(compounds_of_df):
            raise ValueError(
                f"{assigner=} has {assigner.compounds=} which are not in the"
                f" dataframe compounds: {compounds_of_df}"
            )

        if not hasattr(assigner, "runtypes") or assigner.runtypes is None:
            # Set all the runtypes if not specified
            assigner.runtypes = runtypes_from_df(df)

        # Get the rows that the assigner should use
        rows = (
            # Correct types
            df[("-", "type")].isin(assigner.runtypes)
            # Correct times
            & (
                df[("-", "datetime")]
                if ("-", "datetime") in df.columns
                else pd.Series(df.index, index=df.index)
            ).between(assigner.start, assigner.stopp)
        )

        # Check consistency of the df
        if not rows.any():
            raise ValueError(
                f"No rows in the dataframe with {assigner.runtypes=} and between"
                f" {assigner.start=} and {assigner.stopp=}"
            )

        sub_df = df.loc[rows]

        if ("-", "datetime") in sub_df.columns:
            assigner.dt = sub_df[("-", "datetime")]

        assigner.fit(df.loc[rows])

    @staticmethod
    def apply(assigner: AbstractQA_Assigner, df: pd.DataFrame):
        """Apply a QA assigner to a dataframe.

        Args:
            assigner: The QA assigner to apply.
            df: The dataframe to apply the QA assigner to.
        """

        # Get the runtypes that the assigner should use
        runtypes = assigner.runtypes
        # Get the compounds that the assigner should use

        # Get the rows that the assigner should use
        rows = df[("-", "type")].isin(runtypes)

        # Apply the assigner
        flagging_dict = assigner.assign(df.loc[rows])

        if not isinstance(flagging_dict, dict):
            raise ValueError(
                f"The assigner {assigner} did not return a dict but a"
                f" {type(flagging_dict)}"
            )

        logger.debug(f"Assigner {assigner} returned  {flagging_dict}")

        flag(
            df,
            assigner,
            flagging_dict,
            inplace=True,
        )
