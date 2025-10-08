from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import yaml
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AssignerSettings(BaseModel):
    # A unique identifier for the data
    name: str
    # The name of the model that should be used to check the data
    model: str
    # The start of the data that should be used to check
    start: timedelta | datetime | None = None
    stopp: timedelta | datetime | None = None

    params: dict[str, Any] = {}

    def model_post_init(self, __context):
        if isinstance(self.start, timedelta):
            self.start = pd.Timestamp(datetime.now() - self.start)
        elif isinstance(self.start, datetime):
            self.start = pd.Timestamp(self.start)
        elif self.start is None:
            self.start = pd.Timestamp.min

        if isinstance(self.stopp, timedelta):
            self.stopp = pd.Timestamp(datetime.now() - self.stopp)
        elif isinstance(self.stopp, datetime):
            self.stopp = pd.Timestamp(self.stopp)
        elif self.stopp is None:
            self.stopp = pd.Timestamp.max

        if self.start > self.stopp:
            raise ValueError("The start time must be before the stop time.")


def read_setting_file(file_path: os.PathLike) -> list[AssignerSettings]:
    """Read a setting file and return the settings.

    Args:
        file_path: The path to the setting file.

    Returns:
        A list of settings.
    """
    # Read yaml file
    with open(file_path, "r") as file:
        settings = yaml.safe_load(file)
    logger.info(f"Read {settings=}")

    for name, this_settings in settings.items():
        # Add the name in each setting
        if "name" in this_settings:
            raise ValueError(
                f"The setting {name} has a name attribute, which is not allowed."
            )
        this_settings["name"] = name

    return [AssignerSettings(**setting) for setting in settings.values()]
