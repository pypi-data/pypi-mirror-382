import json
import os
from pathlib import Path

import polars as pl

import src.config as cfg
from src.utils import set_plt_rcparams

THIS_DIR = Path(__file__).parent

if __name__ == "__main__":
    with open(os.path.join(THIS_DIR, "params", "MLP.json"), "r") as f:
        params = json.load(f)
    states = params["types"].split(",")
    change_times = (
        pl.read_csv(
            os.path.join(THIS_DIR, "data", "change_times.csv"), has_header=False
        )
        .to_series()
        .to_list()
    )
    n_time_bins = len(change_times) + 1

    set_plt_rcparams()

    log_summary = pl.read_csv(
        os.path.join(cfg.BEAST_LOGS_SUMMARIES_DIR, "fbd-empirical", "MLP.csv")
    )
    for s in states:
        estimates: list[float] = [
            log_summary[f"birthRatei{i}_{s}_median"].median()
            for i in range(n_time_bins)
        ]
        plt.step(change_times, estimates[:-1], label=rf"$\lambda_{{{s}}}$")
        plt.legend()
    plt.gca().invert_xaxis()  # This reverses the x-axis
