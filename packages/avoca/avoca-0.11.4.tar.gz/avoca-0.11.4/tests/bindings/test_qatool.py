from datetime import timedelta
from pathlib import Path

import pandas as pd
import pytest

from avoca.bindings.qa_tool import export_EmpaQATool
from avoca.testing import testdata_dir
from avoca.testing.df import invalids_df, simple_df


@pytest.mark.parametrize(
    "df, name",
    [
        (simple_df, "simple"),
        (invalids_df, "invalids"),
    ],
)
def test_export_EmpaQATool(df, name):
    """Test the export_EmpaQATool function."""

    # Create a test dataframe
    df = df.copy()
    df[("compA", "flag")] = 0
    df[("compB", "flag")] = 0

    df[("-", "datetime")] = pd.date_range(start="2025-01-01", periods=len(df), freq="h")

    # Export the dataframe to a file
    export_path = testdata_dir / "export_empa_qa_tool"
    export_file = export_EmpaQATool(
        df,
        export_path,
        datetime_offsets=(timedelta(minutes=-5), timedelta(minutes=0)),
        station=name,
    )

    # Check that the file is created
    assert Path(export_file).is_file()

    # Read the file and check that the data is correct
    df_exported = pd.read_csv(
        export_file,
        sep=";",
    )
    assert len(df_exported) == len(df)
    # Check that the 'compB-Value' column is of float dtype
    assert pd.api.types.is_float_dtype(df_exported["compB-Value"])
    assert not pd.isna(df_exported["compB-Value"]).any(), "NAN values must be 999..."
