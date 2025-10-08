import pandas as pd
from pandas.api.types import is_integer_dtype

from avoca.flags import QA_Flag
from avoca.qa_class.abstract import AbstractQA_Assigner


def flag(
    df: pd.DataFrame,
    assigner: AbstractQA_Assigner | QA_Flag,
    flagging_dict: dict[str, pd.Index],
    inplace: bool = False,
    variable: str | None = None,
) -> pd.DataFrame:
    """Flag a dataframe with a flagging dictionary.

    Args:
        df: The dataframe to flag.
        assigner: The QA assigner to use.
        flagging_dict: The flagging dictionary to use.
            The keys are the compounds and the values are the indices of the rows to flag.
            The indices are the indices of the rows in the dataframe.

    Returns:
        The flagged dataframe.
    """
    if not inplace:
        df = df.copy()

    if isinstance(assigner, AbstractQA_Assigner):
        flag = assigner.flag
        # Check that the compounds given are in the assigner
        missing_compounds = set(flagging_dict.keys()) - set(assigner.compounds)
        variable = assigner.variable
        if missing_compounds:
            raise ValueError(
                f"The compounds {missing_compounds} are not in the assigner {assigner}"
            )
    elif isinstance(assigner, QA_Flag):
        flag = assigner
        if variable is None:
            raise ValueError(
                "The variable name should be given when using a flag directly"
            )
    else:
        raise TypeError(
            "The assigner should be either a QA_Flag or an AbstractQA_Assigner"
            f" but is {type(assigner)}"
        )

    for c, index in flagging_dict.items():

        flag_col = (c, "flag")
        # Check that the flag column exists in the dataframe
        if flag_col not in df.columns:
            # Add it as an empty column
            df[flag_col] = int(0)
        # Check that the flags are in int format
        elif not is_integer_dtype(df[flag_col].dtype):
            raise ValueError(
                f"The flags for {c} from the test dataframe should be integers"
                f" but are {df[flag_col].dtype=}"
            )
        # Add the flag to the original dataframe using bitwise or
        df.loc[index, flag_col] |= flag.value

    return df
