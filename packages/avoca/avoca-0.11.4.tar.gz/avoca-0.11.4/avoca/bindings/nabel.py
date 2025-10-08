"""NABEL is has simple csv files that we need to read and write."""

import logging
from pathlib import Path
import pandas as pd


logger = logging.getLogger(__name__)


def read_nabel_csv(file_path: Path) -> pd.DataFrame:
    """Read a NABEL csv file."""

    return pd.read_csv(
        file_path,
        sep=";",
        header=0,
        skiprows=[0, 2, 3],
        parse_dates=["Kanal:"],
        date_format="%d.%m.%Y %H:%M",
        index_col="Kanal:",
        encoding="latin1",
    )


def read_nabel_folder(nabel_filepath_pattern: Path) -> pd.DataFrame:
    """Read a NABEL folder.

    :arg nabel_filepath_pattern: Template for the nabel files.
        This must contain a `*` in the name.
        see `pathlib.Path.glob` for more information.

    :returns: A dataframe with all the nabel files concatenated.
    """

    nabel_filepath_pattern = Path(nabel_filepath_pattern)

    nabel_files = list(nabel_filepath_pattern.parent.glob(nabel_filepath_pattern.name))

    if not nabel_files:
        raise FileNotFoundError(f"No files found with pattern {nabel_filepath_pattern}")

    return pd.concat([read_nabel_csv(file) for file in nabel_files]).sort_index()


def add_nabel_data(df: pd.DataFrame, df_nabel: pd.DataFrame) -> pd.DataFrame:
    """Add NABEL data to the dataframe.

    :arg df: Dataframe to add the data to.
    :arg nabel_data: Dataframe with the NABEL data.

    :returns: A new dataframe with the NABEL data added.
    """

    df_out = df.copy()

    col_dt_start = ("StartEndOffsets", "datetime_start")
    col_dt_end = ("StartEndOffsets", "datetime_end")

    if col_dt_start not in df.columns or col_dt_end not in df.columns:
        raise ValueError(
            f"Columns {col_dt_start} and {col_dt_end} not found in dataframe."
        )

    # Check the that the index is datetime
    if not isinstance(df_nabel.index, pd.DatetimeIndex):
        raise ValueError("The dataframe index must be a datetime index.")

    # Select for each row the correct data
    datas = [
        df_nabel.loc[row[col_dt_start] : row[col_dt_end]] for _, row in df.iterrows()
    ]

    df_nabel_values = pd.DataFrame(map(lambda data: data.mean(), datas))
    df_nabel_acc = pd.DataFrame(map(lambda data: data.std(), datas))

    # add the data to the results

    for col in df_nabel_values.columns:
        if col.startswith("Unnamed"):
            # pandas artifact on the last column
            continue
        col_conc = (col, "conc")
        col_flag = (col, "flag")
        col_acc = (col, "u_expanded")
        col_precision = (col, "u_precision")
        columns = [col_conc, col_flag, col_acc, col_precision]

        if any(c in df_out.columns for c in columns):
            logger.warning(f"Column {col} already exists in the results. Skipping.")
            continue

        df_out[col_conc] = df_nabel_values[col]
        df_out[col_acc] = df_nabel_acc[col]
        df_out[col_flag] = int(0)  # No flag
        df_out[col_precision] = float(0.0)  # No precision

    return df_out
