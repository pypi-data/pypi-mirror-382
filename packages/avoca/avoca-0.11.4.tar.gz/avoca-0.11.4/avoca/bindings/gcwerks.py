"""Bindings for gcwerks.



General information about extraction from gcwerks
--------------------------------------------------

You can use gcwerks as a command line:

-gcdir /agage/jungfraujoch-medusa

```
gcexport  GCDIR  -format report.conf  -peaklist peak.list

```

`peak.list` is a text file containing the compounds to export:

```
NF3
HFC-23

```

`report.conf` contains configuration for the export.


A default is found in `config/gcwerks-report.conf`

The following time format numbers may be used in the report.conf file.

    1: yyyy-mm-dd hh:mm
    2: yyyy-mm-dd hh:mm:ss
    3: yymmdd hhmm
    4: yymmdd hhmmss
    5: yyyy mm dd hh mm
    6: yyyy mm dd hh mm ss
    7: yyyy.ffffff (year and fractional year)


Parameters can be decided like

* general
* per comopund

Variables:
* `rt`
* `w`
* `ht`
* `area`
* `norm_ht`
* `norm_a`
* `C_ht`
* `C_a`
* `C`


"""

from __future__ import annotations

import logging
import subprocess
import warnings
from datetime import datetime
from os import PathLike
from pathlib import Path

import numpy as np
import pandas as pd

from avoca.flags import QA_Flag

logger = logging.getLogger(__name__)


class ValidFlag:
    # Just a 'fake' that has the same interface as QA_Flag but value 0 for valid
    value = 0


flag_values = {
    # Star-flagged data should be removed from the data set. These are flags that GCWerks puts automatically when a value is grossly out of line with the bracketing values. Star-flags occur typically for standard measurements, when there is a break in measurements or some other issue. For 'air' measurements, these are not very common. So, you should remove these measurements.
    "*": QA_Flag.INVALIDATED_EXT,
    # H flags denote that the reporting of the substance at that time was done by peak height rather than peak area. So, H-flagged data are perfectly fine to be used as normal measurements. Also, this additional information of 'H' does not need to be propagated. So, for you, it is just to accept this as a valid measurement.
    "H": QA_Flag.HEIGHT_INTEGRATION,
    # B: Often for std. When there is a large change in the std sensitivity, it puts a B flag. For example, after a tune, when the sensitivity is suddenly much higher. GCwerks detects this and flags as B. The B flag is an 'inclusive' flag, ie. the data point is still used for the analysis/calculation.
    "B": ValidFlag,
    # F: An exclusive flag. F-flagged data are not used. F flags are either set by the user during data processing, if something is wrong, and can apply to air or std and can be single points or whole periods. GCWerks is sometimes also flagging data automatically, in the 'Report', they appear as stars/asterisks. These are flagged on the idea of 'outliers', both in air and standard.
    "F": QA_Flag.INVALIDATED_EXT,
    # X: An X flag is an 'un-do' the flag. If there is an automatic flag by GCWerks, but I decide I want that data point still included, I have the option to set an X flag.
    "X": ValidFlag,
}

# Show the flags and the columns they are applied to
flags_allowed = list(flag_values.keys())
# Add the last values allowed in the columns
flags_known = flags_allowed.copy()
flags_known.extend(
    [
        "n",  # From nan
        "f",  # From inf
        *[str(i) for i in range(10)],  # Last number
    ]
)
cols_have_flags = [
    "C",
    "area",
    "rt",
    "ht",
    "w",
]
cols_float = cols_have_flags + ["q1_area", "q2_area"]
cols_zero_is_nan = ["rt"]


# allowed variables
allowed_vars = [
    "area",
    "q1_area",
    "q2_area",
    "rt",
    "C",
    "ht",
    "w",
    "RL.report",
    "norm_ht",
    "norm_a",
    "C_ht",
    "C_a",
    "C.report",
]


def read_gcwerks(
    file_path: PathLike,
    datetime_format: str = "%y%m%d%H%M",
    runtypes: list[str] = [],
    keep_ordering_from_file: bool = False,
    return_flags: bool = True,
) -> pd.DataFrame:
    """Read the input '.dat' file from gcwerks, adding a column: ('-', 'datetime').



    Args:
        file_path: The path to the file to read.
        datetime_format: The format of the datetime in the file.
        runtypes: The run types to keep. If empty, all run types are kept.
        keep_ordering_from_file: Keep the ordering of the columns from the file.
        return_flags: Return the flags in the dataframe.
    """

    file_path = Path(file_path)

    read_csv_kwargs = dict(
        filepath_or_buffer=file_path,
        # Separator
        sep=r"\s+",
        # use the line number 1 and 2 as headers # Line 0 is skipped
        header=[1, 2],
        # Ensure the date an time are read as str
        dtype={("-", "date"): str, ("-", "time"): str},
    )

    successfull_read = False
    while not successfull_read:
        try:
            df = pd.read_csv(**read_csv_kwargs)
            successfull_read = True
        except pd.errors.ParserError as e:
            # Will give something like: Error tokenizing data. C error: Expected 27 fields in line 6, saw 28
            # Get the number of fields expected, the line number and the number of fields seen
            fields_expected = int(str(e).split("Expected ")[1].split(" fields")[0])
            buggy_line = str(e).split("line ")[1].split(",")[0]
            fields_seen = int(str(e).split("saw ")[1])

            logger.debug(f"{fields_expected=} {buggy_line=} {fields_seen=}")

            if "skiprows" not in read_csv_kwargs:
                read_csv_kwargs["skiprows"] = []

            if fields_seen < fields_expected:
                # This line is missing a field, ignore it
                logger.warning(
                    f"Error reading file {file_path}: {e}. Removing line {buggy_line}"
                )
                read_csv_kwargs["skiprows"].append(int(buggy_line) - 1)

            if fields_seen > fields_expected:
                # This line has an extra field, ignore it
                logger.warning(
                    f"Error reading file {file_path}: {e}. Removing starting lines"
                    f" line {buggy_line}"
                )
                read_csv_kwargs["skiprows"].extend(range(3, int(buggy_line) + 2))

            logger.error(f"New skiprows: {read_csv_kwargs['skiprows']}")

    df[("-", "datetime")] = pd.to_datetime(
        # Merge the str for date and time
        df["-", "date"] + df["-", "time"],
        format=datetime_format,
    )

    substances = []

    for col in df.columns:
        sub = col[0]

        if sub != "-":
            if sub not in substances:
                substances.append(sub)
            if return_flags and (sub, "flag") not in df.columns:
                with warnings.catch_warnings():
                    warnings.simplefilter(
                        action="ignore", category=pd.errors.PerformanceWarning
                    )
                    df[(sub, "flag")] = pd.Series(data=0, index=df.index, dtype=int)

        # Make a serie full of 0 = `Valid measurement`
        serie_str: pd.Series = df[col].astype(str)
        # Last character is the flag
        flags: pd.Series = serie_str.str[-1]
        if col[1] in cols_float:
            # Remove the flag value when given
            serie_str = serie_str.apply(
                lambda x: x[:-1] if x[-1] in flags_allowed else x
            )
            # Convert the serie to numeric
            df[col] = pd.to_numeric(serie_str, errors="coerce")

        if col[1] in cols_zero_is_nan:
            # 0 values should be nan
            serie_str = df[col].replace(0, np.nan)

        if col[1] in cols_have_flags:
            # There is a flag

            # Ensure there are no unknown flags
            unknown_flags = flags[~flags.isin(flags_known)].unique()
            if len(unknown_flags):
                raise ValueError(f"Unknown flags for {col}: {unknown_flags}")

            for flag_str, flag_obj in flag_values.items():
                # Add the flag to the serie
                mask_flag = flags == flag_str
                if return_flags:
                    df.loc[mask_flag, (sub, "flag")] |= flag_obj.value

                if flag_obj == QA_Flag.INVALIDATED_EXT:
                    df.loc[mask_flag, col] = np.nan

            if return_flags:
                # where value is nan or inf, the flag is
                # 999 = `Missing measurement, unspecified reason`
                mask_nan = serie_str.isin(["nan", "inf"])
                mask_nan |= df[col].isna()
                df.loc[mask_nan, (sub, "flag")] |= QA_Flag.MISSING.value

    # Set the calibration flag
    type_col = ("-", "type")
    if type_col in df.columns:
        mask_calib = df[("-", "type")].isin(["std"])
        if return_flags:
            for sub in substances:
                df.loc[mask_calib, (sub, "flag")] |= QA_Flag.CALIBRATION.value

        if runtypes:
            df = df[df[("-", "type")].isin(runtypes)]
    else:
        if runtypes:
            logger.warning(
                "No type column found in the data. Run types cannot be filtered as"
                " specified."
            )

    # Sort the columns by the first level
    if not keep_ordering_from_file:
        df = df.sort_index(axis=1, level=0)
    df = df.set_index(("-", "datetime"))
    return df


def export(
    workdir: PathLike,
    gcdir: PathLike,
    compounds: list[str],
    out_file: PathLike,
    date_start: datetime,
    date_end: datetime | None = None,
    variables: list[str] = ["area", "rt", "C"],
    update: bool = False,
    require_import: bool = False,
    verbose: bool = True,
    use_reported_conc: bool = True,
    gc_bin_dir: str = "/agage/gcwerks-3/bin",
):
    """Export the data from gcwerks to a file."""

    workdir = Path(workdir)
    gcdir = Path(gcdir)
    out_file = Path(out_file)

    # The file is in the same directory as this py file
    report_conf = __file__.replace("gcwerks.py", "gcwerks-report.conf")

    logger.debug(f"Exporting data to {out_file}")
    logger.debug(f"{variables=}")
    logger.debug(f"{compounds=}")

    if not variables:
        raise ValueError("No variables selected")
    if not compounds:
        raise ValueError("No compounds selected")

    if date_end is not None:
        if not date_end > date_start:
            raise ValueError(
                f"End date ({date_end}) must be after start date ({date_start})"
            )

    for var in variables:
        if var not in allowed_vars:
            raise ValueError(
                f"Variable {var} not allowed. Allowed variables are: {allowed_vars}"
            )

    if use_reported_conc and "C" in variables:
        variables = variables.copy()
        variables.remove("C")
        variables.append("C.report")

    if update:
        # These are the command to run gc werks and doing the update of the data
        command_runindex = f"{gc_bin_dir}/run-index -gcdir {gcdir}"
        print("Running: ", command_runindex)
        subprocess.run(command_runindex, shell=True, check=True)
        if require_import:
            command_import = f"{gc_bin_dir}/gcimport -gcdir {gcdir}"
            print("Running: ", command_import)
            subprocess.run(command_import, shell=True, check=True)
        command_update = f"{gc_bin_dir}/gcupdate -gcdir {gcdir} -1m"
        print("Running: ", command_update)
        subprocess.run(command_update, shell=True, check=True)
        command_calc = f"{gc_bin_dir}/gccalc -gcdir {gcdir} -1"
        print("Running: ", command_calc)
        subprocess.run(command_calc, shell=True, check=True)

    variables_str = " ".join([f"{sub}.{var}" for sub in compounds for var in variables])

    command = " ".join(
        (
            f"{gc_bin_dir}/gcexport",
            f"-gcdir {gcdir}",
            # f"-format {report_conf}",
            f"-mindate {date_start.strftime('%y%m%d')}",
            (f"-maxdate {date_end.strftime('%y%m%d')}" if date_end else ""),
            "time",
            "type",
            "sample",
            f"{variables_str}",
            f"> {out_file}",
        )
    )
    # command = f"gcnetcdf-export -gcdir {gcdir}  -mindate {date_start.strftime('%y%m%d')} time type {variables_str} -exportdir {out_file.parent}"

    # Run the command
    print("Running: ", command)
    subprocess.run(command, shell=True, check=True)


def get_gcwerks_folders(gcwerks_folders: PathLike = "/agage/") -> list[Path]:
    """Get the folders in the directory contiaining all gcwerks intruments."""

    gcwerks_folders = Path(gcwerks_folders)
    if not gcwerks_folders.is_dir():
        logger = logging.getLogger(__name__)
        logger.error(f"{gcwerks_folders} is not a directory. Cannot get the folders.")
        return []
    return [f for f in gcwerks_folders.iterdir() if f.is_dir()]


def read_quats_log(gcdir: PathLike) -> pd.DataFrame:
    """Read the quat.log file from gcwerks."""

    # Find where the quat log file is located
    quat_log_filepath = Path(gcdir) / "results" / "log" / "quat.log"

    if not quat_log_filepath.exists():
        raise FileNotFoundError(f"File {quat_log_filepath} not found.")

    df = pd.read_csv(
        quat_log_filepath,
        sep=r"\s+",
        skiprows=1,
        header=None,
        names=[
            "dt1",
            "dt2",
            "gas",
            "mean",
            "mean_s",
            "blank",
            "blank_s",
            "fit_n",
            "fit_a",
            "fit_b",
            "fit_c",
            "#",
            "tanks",
        ],
    )
    # Convert datetime from unix timestamp to datetime
    for col in ["dt1", "dt2"]:
        df[col] = pd.to_datetime(df[col], unit="s")

    # Split the tank column inot the two tanks they contain
    splitted = df["tanks"].str.split("/", expand=True)
    df["sampleQuaternary"] = splitted[0]
    df["sampleTertiary"] = splitted[1]

    return df


def to_gcwerks_dat(
    df: pd.DataFrame,
    file_path: PathLike,
) -> None:
    """Write the data to a gcwerks '.dat' file."""

    df = df.copy()

    if ("-", "date") not in df.columns:
        df[("-", "date")] = df[("-", "datetime")].dt.strftime("%y%m%d")
    if ("-", "time") not in df.columns:
        df[("-", "time")] = df[("-", "datetime")].dt.strftime("%H%M")

    if ("-", "datetime") in df.columns:
        df = df.drop(("-", "datetime"), axis=1)

    with open(file_path, "w") as f:
        f.write(f"# Created by avoca on {datetime.now()}\n")
        df.to_csv(f, sep=" ", index=False, lineterminator="\n", na_rep="nan")
