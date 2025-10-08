"""Store dataframes for testing purposes.

We try to follow always the same pattern for the dataframes:

* 2 compounds (compA and compB)
* compA is the
"""

import numpy as np
import pandas as pd

empty_index = pd.Index([], dtype="int64")

simple_df = pd.DataFrame(
    np.ones((2, 4)),
    columns=pd.MultiIndex.from_tuples(
        [
            ("compA", "area"),
            ("compA", "C"),
            ("compB", "area"),
            ("compB", "C"),
        ]
    ),
)

invalids_df = pd.DataFrame(
    np.transpose([[1.0, 1.1, 0.8, 0.9], [1.0, np.inf, np.nan, -0.3]]),
    columns=pd.MultiIndex.from_tuples(
        [
            ("compA", "C"),
            ("compB", "C"),
        ]
    ),
)

compab_multiindex = pd.MultiIndex.from_tuples(
    [
        ("compA", "test_var"),
        ("compB", "test_var"),
    ]
)

make_compab_df = lambda x: pd.DataFrame(
    np.array(x).T,
    columns=compab_multiindex,
)

df_regular = make_compab_df(
    [
        # Add here an extreme value
        [1.0, 1.1, 0.8, 0.9, 1.2, 1.1, 0.8, 1.0],
        [0.9, 1.1, 0.9, 1.1, 1.0, 1.1, 0.9, 1.1],
    ]
)

df_one_extreme = make_compab_df(
    [
        # Add here an extreme value
        [1.0, 1.1, 10.0],
        [1.0, 1.1, 0.9],
    ]
)


df_nan_training = make_compab_df(
    [
        # Add here one nan value
        [1.0, 1.1, np.nan],
        [1.0, 1.1, 0.9],
    ]
)

df_full_nan = make_compab_df(
    [
        # Full of nans
        [np.nan, np.nan, np.nan],
        [1.0, 1.1, 0.9],
    ]
)

df_with_inf = make_compab_df(
    [
        # Add here one inf value
        [1.0, 1.1, np.inf],
        [1.0, 1.1, 0.9],
    ]
)

# Around zero, with also negative values can be tricky so we want to test it
df_around_zero = df_regular - 1.0
