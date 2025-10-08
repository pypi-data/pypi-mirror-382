from pathlib import Path

from avoca.bindings.gcwerks import read_gcwerks

this_dir = Path(__file__).parent


def test_read_gcwerks():
    path = this_dir / "gcwerks.dat"
    df = read_gcwerks(path)
    assert len(df) == 4
