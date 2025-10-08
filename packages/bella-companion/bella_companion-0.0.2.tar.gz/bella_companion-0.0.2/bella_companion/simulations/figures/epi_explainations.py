import os
from functools import partial

import joblib
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import src.config as cfg
from lumiere.backend import sigmoid
from src.simulations.figures.utils import (
    plot_partial_dependencies,
    plot_shap_features_importance,
)
from src.simulations.scenarios.epi_multitype import (
    MIGRATION_PREDICTOR,
    MIGRATION_RATE_UPPER,
    MIGRATION_RATES,
    SCENARIO,
)
from src.utils import set_plt_rcparams


def set_plt_rcparams():
    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["xtick.labelsize"] = 14
    plt.rcParams["ytick.labelsize"] = 14
    plt.rcParams["font.size"] = 14
    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["lines.linewidth"] = 3


def _plot_predictions(log_summary: pl.DataFrame, output_dir: str):
    sort_idx = np.argsort(MIGRATION_PREDICTOR.flatten())

    estimates = np.array(
        [
            log_summary[f"{target}_median"].median()
            for target in SCENARIO.targets["migrationRate"]
        ]
    )
    lower = np.array(
        [
            log_summary[f"{target}_lower"].median()
            for target in SCENARIO.targets["migrationRate"]
        ]
    )
    upper = np.array(
        [
            log_summary[f"{target}_upper"].median()
            for target in SCENARIO.targets["migrationRate"]
        ]
    )
    plt.errorbar(
        MIGRATION_PREDICTOR.flatten()[sort_idx],
        estimates[sort_idx],
        yerr=[
            estimates[sort_idx] - lower[sort_idx],
            upper[sort_idx] - estimates[sort_idx],
        ],
        marker="o",
        color="C2",
    )
    plt.plot(
        MIGRATION_PREDICTOR.flatten()[sort_idx],
        estimates[sort_idx],
        marker="o",
        color="C2",
    )
    plt.plot(
        MIGRATION_PREDICTOR.flatten()[sort_idx],
        MIGRATION_RATES.flatten()[sort_idx],
        linestyle="dashed",
        marker="o",
        color="k",
    )
    plt.xlabel("Migration predictor")
    plt.ylabel("Migration rate")
    plt.savefig(os.path.join(output_dir, "predictions.svg"))
    plt.close()


def main():
    output_dir = os.path.join(cfg.FIGURES_DIR, "epi-explainations")
    os.makedirs(output_dir, exist_ok=True)

    log_dir = os.path.join(cfg.BEAST_LOGS_SUMMARIES_DIR, "epi-multitype")
    model = "MLP-32_16"
    log_summary = pl.read_csv(os.path.join(log_dir, f"{model}.csv"))
    weights = joblib.load(os.path.join(log_dir, f"{model}_weights.pkl"))

    set_plt_rcparams()

    _plot_predictions(log_summary, output_dir)
    plot_partial_dependencies(
        weights=weights["migrationRate"],
        features=SCENARIO.features["migrationRate"],
        output_dir=output_dir,
        output_activation=partial(sigmoid, upper=MIGRATION_RATE_UPPER),
    )
    plot_shap_features_importance(
        weights=weights["migrationRate"],
        features=SCENARIO.features["migrationRate"],
        output_file=os.path.join(output_dir, "shap_values.svg"),
        output_activation=partial(sigmoid, upper=MIGRATION_RATE_UPPER),
    )


if __name__ == "__main__":
    main()
