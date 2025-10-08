import os

import matplotlib.pyplot as plt
import polars as pl

import src.config as cfg
from src.simulations.figures.utils import (
    plot_coverage_per_time_bin,
    plot_maes_per_time_bin,
    step,
)
from src.simulations.scenarios.epi_skyline import REPRODUCTION_NUMBERS
from src.utils import set_plt_rcparams


def main():
    output_dir = os.path.join(cfg.FIGURES_DIR, "epi-predictions")
    os.makedirs(output_dir, exist_ok=True)

    set_plt_rcparams()

    for i, reproduction_number in enumerate(REPRODUCTION_NUMBERS, start=1):
        summaries_dir = os.path.join(cfg.BEAST_LOGS_SUMMARIES_DIR, f"epi-skyline_{i}")
        logs_summaries = {
            "Nonparametric": pl.read_csv(
                os.path.join(summaries_dir, "Nonparametric.csv")
            ),
            "GLM": pl.read_csv(os.path.join(summaries_dir, "GLM.csv")),
            "MLP": pl.read_csv(os.path.join(summaries_dir, "MLP-16_8.csv")),
        }
        true_values = {"reproductionNumber": reproduction_number}

        for log_summary in logs_summaries.values():
            step(
                [
                    log_summary[f"reproductionNumberi{i}_median"].median()
                    for i in range(len(reproduction_number))
                ]
            )
        step(reproduction_number, color="k", linestyle="--")
        plt.ylabel("Reproduction number")
        plt.savefig(os.path.join(output_dir, f"epi-skyline_{i}-predictions.svg"))
        plt.close()

        plot_coverage_per_time_bin(
            logs_summaries,
            true_values,
            os.path.join(output_dir, f"epi-skyline_{i}-coverage.svg"),
        )
        plot_maes_per_time_bin(
            logs_summaries,
            true_values,
            os.path.join(output_dir, f"epi-skyline_{i}-maes.svg"),
        )


if __name__ == "__main__":
    main()
