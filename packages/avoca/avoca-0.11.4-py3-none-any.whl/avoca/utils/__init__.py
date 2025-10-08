from __future__ import annotations
from contextlib import contextmanager

import pandas as pd


def compounds_from_df(df: pd.DataFrame) -> list[str]:
    """Get the compounds from a dataframe.

    Args:
        df: The dataframe to get the compounds from.

    Returns:
        The compounds in the dataframe.
    """
    return [c for c in df.columns.get_level_values(0).unique() if c != "-"]


def runtypes_from_df(df: pd.DataFrame) -> list[str]:
    """Get the runtypes from a dataframe.

    Args:
        df: The dataframe to get the runtypes from.

    Returns:
        The runtypes in the dataframe.
    """
    return list(df[("-", "type")].unique())


@contextmanager
def datetime_for_index(df):
    """Context manager to set the datetime as the index of a dataframe.

    Usage:
    ```
    with datetime_for_index(df):
        # Do something with the dataframe
        df...

    # The dataframe will be reverted back to the original index
    df
    ```

    """
    original_index = df.index
    original_column = df[("-", "datetime")]
    df.set_index(("-", "datetime"), inplace=True)

    try:
        yield df
    finally:
        # Revert back to the original index
        df.index.name = None
        df.set_index(original_index, inplace=True)
        df.index.name = None
        df[("-", "datetime")] = original_column
