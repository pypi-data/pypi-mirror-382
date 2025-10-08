import os

import matplotlib.pyplot as plt
import polars as pl

import src.config as cfg
from src.simulations.figures.utils import (
    plot_coverage_per_time_bin,
    plot_maes_per_time_bin,
    step,
)
from src.simulations.scenarios.fbd_no_traits import BIRTH_RATES, DEATH_RATES
from src.utils import set_plt_rcparams


def main():
    output_dir = os.path.join(cfg.FIGURES_DIR, "fbd-predictions")
    os.makedirs(output_dir, exist_ok=True)

    set_plt_rcparams()

    for i, (birth_rate, death_rate) in enumerate(
        zip(BIRTH_RATES, DEATH_RATES), start=1
    ):
        summaries_dir = os.path.join(cfg.BEAST_LOGS_SUMMARIES_DIR, f"fbd-no-traits_{i}")
        logs_summaries = {
            "Nonparametric": pl.read_csv(
                os.path.join(summaries_dir, "Nonparametric.csv")
            ),
            "GLM": pl.read_csv(os.path.join(summaries_dir, "GLM.csv")),
            "MLP": pl.read_csv(os.path.join(summaries_dir, "MLP-16_8.csv")),
        }
        true_values = {"birthRate": birth_rate, "deathRate": death_rate}

        for id, rate in true_values.items():
            for log_summary in logs_summaries.values():
                step(
                    [
                        log_summary[f"{id}i{i}_median"].median()
                        for i in range(len(rate))
                    ],
                    reverse_xticks=True,
                )
            step(rate, color="k", linestyle="--", reverse_xticks=True)
            plt.ylabel(r"$\lambda$" if id == "birthRate" else r"$\mu$")
            plt.savefig(
                os.path.join(output_dir, f"fbd-no-traits_{i}-predictions-{id}.svg")
            )
            plt.close()

        plot_coverage_per_time_bin(
            logs_summaries,
            true_values,
            os.path.join(output_dir, f"fbd-no-traits_{i}-coverage.svg"),
            reverse_xticks=True,
        )
        plot_maes_per_time_bin(
            logs_summaries,
            true_values,
            os.path.join(output_dir, f"fbd-no-traits_{i}-maes.svg"),
            reverse_xticks=True,
        )


if __name__ == "__main__":
    main()
