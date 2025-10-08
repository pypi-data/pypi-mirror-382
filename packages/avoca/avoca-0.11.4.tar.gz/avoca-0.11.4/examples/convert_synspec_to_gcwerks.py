import pandas as pd

from avoca.bindings.gcwerks import to_gcwerks_dat
from avoca.bindings.synspec import read_synspec

files = [
    r"C:\Users\coli\Downloads\VALIDATIONRUNS.TXT",
    r"C:\Users\coli\Downloads\RD202408.TXT",
]
df = pd.concat([read_synspec(f) for f in files], axis="rows").sort_values(
    ("-", "datetime")
)

to_gcwerks_dat(df, r"C:\Users\coli\Downloads\synspec.dat")
