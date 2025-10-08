from pathlib import Path

import pandas as pd

# ISO 8601 date format
date_format = "%Y-%m-%d %H:%M:%S"


def to_csv(df: pd.DataFrame, path: Path, **kwargs) -> None:
    """Export a dataframe to a csv file."""
    df.to_csv(path, index=False, date_format=date_format, **kwargs)


def from_csv(path: Path) -> pd.DataFrame:
    """Read a csv file to a dataframe."""
    df = pd.read_csv(path, header=[0, 1])
    parse_dates = [("-", "datetime"), ("-", "start_datetime"), ("-", "end_datetime")]
    # Convert the datetime column to a datetime object
    for col in parse_dates:
        if col not in df.columns:
            continue
        df[col] = pd.to_datetime(df[col], format=date_format)
    return df
