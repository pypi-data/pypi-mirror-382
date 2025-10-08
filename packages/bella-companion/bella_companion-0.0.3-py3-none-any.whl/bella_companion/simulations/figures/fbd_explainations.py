import ast
import os
from functools import partial

import joblib
import matplotlib.pyplot as plt
import polars as pl
from joblib import Parallel, delayed
from lumiere.backend import sigmoid

import src.config as cfg
from src.figures.utils import (
    plot_partial_dependencies,
    plot_shap_features_importance,
    step,
)
from src.simulations.scenarios.fbd_2traits import (
    BIRTH_RATE_TRAIT1_SET,
    BIRTH_RATE_TRAIT1_UNSET,
    DEATH_RATE_TRAIT1_SET,
    DEATH_RATE_TRAIT1_UNSET,
    FBD_RATE_UPPER,
    N_TIME_BINS,
    SCENARIO,
    STATES,
)
from src.utils import set_plt_rcparams


def _plot_predictions(log_summary: pl.DataFrame, output_dir: str):
    for rate in ["birth", "death"]:
        label = r"\lambda" if rate == "birth" else r"\mu"
        rate_trait_1_set = (
            BIRTH_RATE_TRAIT1_UNSET if rate == "birth" else DEATH_RATE_TRAIT1_UNSET
        )
        rate_trait_1_unset = (
            BIRTH_RATE_TRAIT1_SET if rate == "birth" else DEATH_RATE_TRAIT1_SET
        )
        for state in STATES:
            estimates = [
                log_summary[f"{rate}Ratei{i}_{state}_median"].median()
                for i in range(N_TIME_BINS)
            ]
            step(
                estimates,
                label=rf"${label}_{{{state[0]},{state[1]}}}$",
                reverse_xticks=True,
            )
        step(
            rate_trait_1_unset,
            color="k",
            linestyle="dashed",
            label=rf"${label}_{{0,0}}$ = ${label}_{{0,1}}$",
            reverse_xticks=True,
        )
        step(
            rate_trait_1_set,
            color="gray",
            linestyle="dashed",
            label=rf"${label}_{{1,0}}$ = ${label}_{{1,1}}$",
            reverse_xticks=True,
        )
        plt.legend()
        plt.ylabel(rf"${label}$")
        plt.savefig(os.path.join(output_dir, rate, "predictions.svg"))
        plt.close()


def main():
    output_dir = os.path.join(cfg.FIGURES_DIR, "fbd-explainations")
    for rate in ["birth", "death"]:
        os.makedirs(os.path.join(output_dir, rate), exist_ok=True)

    log_dir = os.path.join(cfg.BEAST_LOGS_SUMMARIES_DIR, "fbd-2traits")
    model = "MLP-32_16"
    log_summary = pl.read_csv(os.path.join(log_dir, f"{model}.csv"))
    weights = joblib.load(os.path.join(log_dir, f"{model}_weights.pkl"))

    set_plt_rcparams()

    _plot_predictions(log_summary, output_dir)

    for rate in ["birth", "death"]:
        plot_partial_dependencies(
            weights=weights[f"{rate}Rate"],
            features=SCENARIO.features[f"{rate}Rate"],
            output_dir=os.path.join(output_dir, rate),
            output_activation=partial(sigmoid, upper=FBD_RATE_UPPER),
        )
        plot_shap_features_importance(
            weights=weights[f"{rate}Rate"],
            features=SCENARIO.features[f"{rate}Rate"],
            output_file=os.path.join(output_dir, rate, "shap_values.svg"),
            output_activation=partial(sigmoid, upper=FBD_RATE_UPPER),
        )


if __name__ == "__main__":
    main()
