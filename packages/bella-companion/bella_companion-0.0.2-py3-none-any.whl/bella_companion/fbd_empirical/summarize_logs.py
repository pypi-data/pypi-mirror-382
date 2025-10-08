import json
import os
from pathlib import Path

import joblib
import polars as pl

from src.config import BEAST_LOGS_SUMMARIES_DIR, BEAST_OUTPUTS_DIR
from src.utils import summarize_logs

THIS_DIR = Path(__file__).parent


def main():
    summaries_dir = os.path.join(BEAST_LOGS_SUMMARIES_DIR, "fbd-empirical")
    os.makedirs(summaries_dir, exist_ok=True)

    with open(os.path.join(THIS_DIR, "params", "MLP.json"), "r") as f:
        params = json.load(f)
    hidden_nodes = list(map(int, params["nodes"].split()))[:-1]
    print(hidden_nodes)
    states = params["types"].split(",")
    logs_dir = os.path.join(BEAST_OUTPUTS_DIR, "fbd-empirical", "MLP")
    change_times = (
        pl.read_csv(
            os.path.join(THIS_DIR, "data", "change_times.csv"), has_header=False
        )
        .to_series()
        .to_list()
    )
    n_time_bins = len(change_times) + 1
    logs_summary, weights = summarize_logs(
        logs_dir,
        target_columns=[
            f"{rate}Ratei{i}_{s}"
            for rate in ["birth", "death"]
            for i in range(n_time_bins)
            for s in states
        ],
        hidden_nodes=hidden_nodes,
        n_features={f"{rate}Rate": 2 for rate in ["birth", "death"]},
        layers_range_start=0,
    )

    logs_summary.write_csv(os.path.join(summaries_dir, f"MLP.csv"))
    joblib.dump(weights, os.path.join(summaries_dir, "weights.pkl"))


if __name__ == "__main__":
    main()
