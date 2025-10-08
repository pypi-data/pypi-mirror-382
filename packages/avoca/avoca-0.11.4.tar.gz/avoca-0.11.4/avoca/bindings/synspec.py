import os

import pandas as pd


def read_synspec(file: os.PathLike, drop_bad_data: bool = False) -> pd.DataFrame:
    """Read a file from a gc955 from synspec.

    :arg file: Path to the file.
    :arg drop_bad_data: Remove bad data from the file (where /Code = B).
        If True, bad data is removed.
        If False, bad data is kept and assumed to be air.

    :returns: A DataFrame with the data.

    """
    if not os.path.exists(file):
        raise FileNotFoundError(f"File {file} does not exist.")
    df = pd.read_csv(
        file,
        encoding="latin1",
        sep=r"\t\s",
        header=1,
        index_col=False,
        engine="python",
        na_values="XXXX",
    )

    # /Codes:
    # C = Calibrationdata
    # N = Normaldata
    # V = Validationdata
    # B = Baddata
    if drop_bad_data:
        mask_baddata = df["/Code"] == "B"
        if mask_baddata.any():
            df = df.loc[~mask_baddata]
    runtype = df["/Code"].replace(
        {
            "V": "std",
            "N": "air",
            "C": "std",
            "S": "tank",
            "B": "air",
        }
    )
    datetime = pd.to_datetime(df["Date"] + df["Time"], format="%d-%m-%y%H:%M")
    substances = [col[5:] for col in df.columns if col.startswith("Area-")]
    area_cols = {(sub, "area"): df[f"Area-{sub}"] for sub in substances}
    conc_cols = {(sub, "conc"): df[f"Conc-{sub}"] for sub in substances}
    rt_cols = {(sub, "rt"): df[f"Reti-{sub}"] for sub in substances}
    return pd.DataFrame(
        {
            ("-", "datetime"): datetime,
            ("-", "type"): runtype,
        }
        | area_cols
        | conc_cols
        | rt_cols
    )
