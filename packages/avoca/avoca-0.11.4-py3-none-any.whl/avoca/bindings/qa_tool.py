"""Few modules for importing and exporting from https://voc-qc.nilu.no/

Originally taken from tucavoc.
"""

import logging
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pandas.errors

from avoca.bindings.ebas_flags import flag_order, flags_to_ebas
from avoca.flags import QA_Flag
from avoca.utils import compounds_from_df


def number_of_digits_required(serie: pd.Series) -> int:
    """Return the number of digits required for the calculation"""
    # TODO: need to check if we need the actual int  value, we can put a .9 at the end
    if all(pd.isna(serie) | (serie == 0)):
        # Only 2 will be required
        return 2
    else:
        number_of_digits = np.log10(serie[serie > 0])
        max_digits = number_of_digits[number_of_digits != np.inf]
        if len(max_digits) == 0:
            return 2
        return int(max(np.max(max_digits), 0) + 2)


def export_EmpaQATool(
    df: pd.DataFrame,
    export_path: Path,
    station: str = "XXX",
    revision_date: datetime | None = None,
    dataset: datetime | str | None = None,
    export_names: dict[str, str] = {},
    datetime_offsets: tuple[timedelta, timedelta] | None = None,
    substances: list[str] = [],
    rounding_decimals: int = 4,
) -> Path:
    """Export to the EmpaQATool format.

    The exported file from the program can then be imported to
    the tool on https://voc-qc.nilu.no/Import
    The specs fro that file can be found in
    https://voc-qc.nilu.no/doc/CSVImport_FormatSpecifications.pdf

    This will add the additional data from the dataframe.

    The file genereated will be named:
    export_path/[station]_[dataset]_[revision].csv

    :arg df: Calculation dataframe
    :arg export_path: Path (directory) to export the file
    :arg station: Station name to use in the file name
    :arg revision_date: Revision date as datetime to use in the file name
    :arg dataset: Dataset name as datetime or string to use in the file name
    :arg export_names: Dictionary of substance names to use in the file name
        The keys are the substance names and the values are the names to use in the file.
    :arg datetime_offsets: Tuple of two timedelta to use for the start and end datetime
    :arg substances: List of substances to export. You can also specify group names.
        If not specified, this will use the substances from `df_substances`.
    :arg rounding_decimals: Number of decimals to round the values to.

    """

    logger = logging.getLogger(__name__)

    warnings.filterwarnings(
        action="ignore",
        category=pandas.errors.PerformanceWarning,
        module="pandas",
    )

    # fmt = "%Y-%m-%d %H:%M:%S"
    fmt = "%d.%m.%Y %H:%M:%S"

    need_datetime_col = ("-", "datetime_start") not in df.columns and (
        "-",
        "datetime_end",
    ) not in df.columns

    if need_datetime_col:
        if ("-", "datetime") not in df.columns:
            df[("-", "datetime")] = df.index
        # Check type of the datetime column
        if not pd.api.types.is_datetime64_any_dtype(df[("-", "datetime")]):
            raise ValueError(
                "The datetime column is not of type datetime64. "
                "Please convert it to datetime64."
                "Or provide ()"
            )
        if datetime_offsets is None:
            raise ValueError(
                "No datetime_start or datetime_end column in the dataframe. "
                "Please provide the datetime_offsets to specify."
            )

        df[("-", "datetime_start")] = df[("-", "datetime")] + datetime_offsets[0]
        df[("-", "datetime_end")] = df[("-", "datetime")] + datetime_offsets[1]

    df_out = pd.DataFrame(
        {
            "start": df[("-", "datetime_start")].dt.strftime(fmt),
            "end": df[("-", "datetime_end")].dt.strftime(fmt),
        },
        index=df.index,
    )
    logger.debug(f"df_out: {df_out.head()}")
    if not substances:
        substances = compounds_from_df(df)

    remove_infs = lambda x: x.replace([np.inf, -np.inf], np.nan)
    is_invalid = lambda x: x.isin([np.inf, -np.inf]) | pd.isna(x)
    clean_col = lambda x: remove_infs(x).round(rounding_decimals).astype(str)

    for substance in substances:

        export_name = export_names.get(substance, substance)

        conc_col = (
            (substance, "conc")
            if (substance, "conc") in df.columns
            else (substance, "C")
        )
        u_expanded_col = (substance, "u_expanded")
        u_precision_col = (substance, "u_precision")
        flag_col = (substance, "flag")

        mask_invalid = (
            (
                df[flag_col] & (QA_Flag.MISSING.value + QA_Flag.INVALIDATED_EXT.value)
            ).astype(bool)
            | is_invalid(df[conc_col])
            | (
                is_invalid(df[u_expanded_col])
                if u_expanded_col in df.columns
                else False
            )
            | (
                is_invalid(df[u_precision_col])
                if u_precision_col in df.columns
                else False
            )
        )

        logger.debug(f"mask_invalid: {mask_invalid}")
        # Flag the invalids
        df.loc[mask_invalid, flag_col] ^= QA_Flag.INVALID_VALUES.value

        # Convert to str so we can control the formatting
        df_out[f"{export_name}-Value"] = clean_col(df[conc_col])

        # Input the missing values as 9. see issue #7 gitlab.empa.ch
        df_out.loc[mask_invalid, f"{export_name}-Value"] = (
            "9" * number_of_digits_required(df[conc_col])
        )

        if u_expanded_col in df.columns:
            # Convert to str so we can control the formatting
            df_out[f"{export_name}-Accuracy"] = clean_col(df[u_expanded_col])
            # Input the missing values as 9. see issue #7 gitlab.empa.ch
            df_out.loc[mask_invalid, f"{export_name}-Accuracy"] = (
                "9" * number_of_digits_required(df[u_expanded_col])
            )

        if u_precision_col in df.columns:
            # Convert to str so we can control the formatting
            df_out[f"{export_name}-Precision"] = clean_col(df[u_precision_col])

            # Input the missing values as 9. see issue #7 gitlab.empa.ch
            df_out.loc[mask_invalid, f"{export_name}-Precision"] = (
                "9" * number_of_digits_required(df[u_precision_col])
            )

        flag_col_out = f"{export_name}-Flag"
        df_out[flag_col_out] = 0.0
        for flag in flag_order:
            df_out.loc[
                (df[flag_col].values & flag.value).astype(bool), flag_col_out
            ] = flags_to_ebas[flag]
        df_out[flag_col_out] = (df_out[flag_col_out] * 1e-3).map("{:.3f}".format)

    export_path.mkdir(exist_ok=True)

    dt_format = "%Y%m%d"
    if dataset is None:
        dataset = datetime.strptime(df_out["start"].iloc[0], fmt).strftime(dt_format)

    if revision_date is None:
        revision_date = datetime.now().strftime(dt_format)

    # [station]_[dataset]_[revision]
    file_name = f"{station}_{dataset}_{revision_date}"

    out_filepath = Path(export_path, file_name).with_suffix(".csv")
    df_out.to_csv(
        out_filepath,
        sep=";",
        index=False,
        encoding="utf-8",
    )
    logger.info(f"Exported to `{out_filepath}`")

    return out_filepath
