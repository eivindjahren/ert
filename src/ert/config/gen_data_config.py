from dataclasses import dataclass
from pathlib import Path
from typing import Union

import numpy as np
import xarray as xr
from sortedcontainers import SortedList

from ert.config.response_config import ResponseConfig


@dataclass
class GenDataConfig(ResponseConfig):
    input_file: str = ""
    report_steps: SortedList = SortedList()

    def __post_init__(self) -> None:
        self.report_steps = (
            SortedList([0])
            if not self.report_steps
            else SortedList(set(self.report_steps))
        )

    def read_from_file(self, run_path: str, _: int) -> Union[xr.Dataset, xr.DataArray]:
        errors = []
        datasets = []
        filename_fmt = self.input_file
        run_path = Path(run_path)
        for report_step in self.report_steps:
            filename = filename_fmt % report_step
            if not Path.exists(run_path / filename):
                errors.append(f"{self.name} report step {report_step} missing")
                continue

            data = np.loadtxt(run_path / filename, ndmin=1)
            active_information_file = run_path / (filename + "_active")
            if active_information_file.exists():
                index_list = np.flatnonzero(np.loadtxt(active_information_file))
                data = data[index_list]
            else:
                index_list = np.arange(len(data))
            datasets.append(
                xr.Dataset(
                    {"values": (["report_step", "index"], [data])},
                    coords={"index": index_list, "report_step": [report_step]},
                )
            )
        if errors:
            raise ValueError(f"Missing files: {errors}")
        return xr.combine_by_coords(datasets)
