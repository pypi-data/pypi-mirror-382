import pandas as pd

from avoca.manager import AssignerManager
from avoca.settings import AssignerSettings
from avoca.testing.df import df_regular


def test_workflow():

    # The assigner manager needs additional columns
    df = df_regular.copy()
    df[("-", "type")] = "test"
    df[("-", "datetime")] = pd.date_range(start="2023-01-01", periods=len(df), freq="h")

    assigner = AssignerManager.create(
        settings=AssignerSettings(
            **{
                "name": "TestAssigner",
                "model": "ExtremeValues",
                "params": {"compounds": ["compA", "compB"], "variable": "test_var"},
            }
        )
    )

    AssignerManager.train(
        assigner=assigner,
        df=df,
    )

    AssignerManager.apply(
        assigner=assigner,
        df=df,
    )
