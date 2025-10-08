"""Test the flagging function."""

import pandas as pd
from pandas.api.types import is_integer_dtype

from avoca.flagging import flag
from avoca.flags import QA_Flag
from avoca.testing.df import df_regular


def test_flagging():

    df_flagged = flag(
        df_regular,
        QA_Flag.INVALIDATED_EXT,
        {
            "compA": pd.Index([2, 3]),
        },
        variable="test_var",
    )

    # Check that the flag column is added
    assert ("compA", "flag") in df_flagged.columns
    # Check that the flag column is of int type
    assert is_integer_dtype(df_flagged[("compA", "flag")].dtype)
    # Check that the flagged rows are set to 1
    assert (
        df_flagged[("compA", "flag")].iloc[[2, 3]] == QA_Flag.INVALIDATED_EXT.value
    ).all()
    # Check that the other rows are set to 0
    assert (df_flagged[("compA", "flag")].iloc[[0, 1, 4]] == 0).all()
