from avoca import io
from avoca.testing import testdata_dir
from avoca.testing.df import simple_df


def test_from_to_csv():
    # Store the dataframe
    io.to_csv(simple_df, "simple_df.csv")
    # Read the dataframe
    df = io.from_csv("simple_df.csv")
    # Check if the dataframes are equal
    assert simple_df.equals(df)


def test_missing_area():
    # This is a file with some missing area columns
    # we should be able to read it
    df = io.from_csv(testdata_dir / "missing_area_cols.csv")
