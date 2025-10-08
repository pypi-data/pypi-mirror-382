"""Small script that shows how to export the data using gcwerks export."""
from datetime import datetime, timedelta
from pathlib import Path


from avoca.bindings.gcwerks import export
# The working directory where all the data is stored
# Use one directory for each kind of data/process you export
gcdir = "/agage/jungfraujoch-medusa"

work_dir = Path("/home/klima/coli/qa/jfj") 
work_dir.mkdir(exist_ok=True)


# as a list of compounds to export
compounds = [
    "CFC-113",
    "CFC-113.q1",
    "CFC-113.q2",
    "CFC-113a",
    "CFC-113a.q1",
    "CFC-113a.q2",
]




out_file = work_dir / "data_CFC113.dat"

# Export the data from gcwerks
export(
    workdir=work_dir,
    gcdir=gcdir,
    compounds = compounds,
    variables=["area", "rt", "C"],
    out_file=out_file,
    date_start=datetime(2022, 1, 1),
    update=False,
    verbose=False,
)


print(f"Data exported to {out_file}")
