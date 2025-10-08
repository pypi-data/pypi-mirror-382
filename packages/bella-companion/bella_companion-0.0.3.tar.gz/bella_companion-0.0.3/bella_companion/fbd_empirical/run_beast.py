import os
from pathlib import Path

import numpy as np
import polars as pl
from phylogenie import load_newick
from phylogenie.utils import get_node_depths
from tqdm import tqdm

import src.config as cfg
from src.utils import run_sbatch

THIS_DIR = Path(__file__).parent


def main():
    output_dir = cfg.BEAST_OUTPUTS_DIR / "fbd-empirical"
    os.makedirs(output_dir, exist_ok=True)

    tree_file = THIS_DIR / "data" / "trees.nwk"
    change_times_file = THIS_DIR / "data" / "change_times.csv"
    sampling_change_times_file = THIS_DIR / "data" / "sampling_change_times.csv"

    change_times = (
        pl.read_csv(change_times_file, has_header=False).to_series().to_numpy()
    )
    time_predictor = " ".join(
        list(map(str, np.repeat(np.insert(change_times, 0, 0), 4)))
    )
    body_mass_predictor = " ".join(["0", "1", "2", "3"] * (len(change_times) + 1))

    trees = load_newick(str(tree_file))
    assert isinstance(trees, list)
    for i, tree in enumerate(tqdm(trees)):
        process_length = max(get_node_depths(tree).values())
        for model in ["hidden-relu", "hidden-tanh"]:
            command = " ".join(
                [
                    cfg.RUN_BEAST,
                    f'-D treeFile={tree_file},treeIndex={i},typeTraitFile={THIS_DIR / "data" / "body_mass.csv"},changeTimesFile={change_times_file},samplingChangeTimesFile={sampling_change_times_file},processLength={process_length},timePredictor="{time_predictor}",bodyMassPredictor="{body_mass_predictor}"',
                    f"-DF {THIS_DIR / 'params.json'}",
                    f"-prefix {output_dir / model}",
                    str(cfg.BEAST_CONFIGS_DIR / "fbd-empirical" / f"{model}.xml"),
                ]
            )
            run_sbatch(
                command,
                cfg.SBATCH_LOGS_DIR / "fbd-empirical" / model / str(i),
                mem_per_cpu="12000",
            )


if __name__ == "__main__":
    main()
