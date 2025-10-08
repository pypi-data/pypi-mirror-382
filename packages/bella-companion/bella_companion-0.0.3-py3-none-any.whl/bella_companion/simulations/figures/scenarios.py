import os

import matplotlib.pyplot as plt
import numpy as np

import src.config as cfg
from src.simulations.figures.utils import step
from src.simulations.scenarios.epi_multitype import MIGRATION_PREDICTOR, MIGRATION_RATES
from src.simulations.scenarios.epi_skyline import REPRODUCTION_NUMBERS
from src.simulations.scenarios.fbd_2traits import (
    BIRTH_RATE_TRAIT1_SET,
    BIRTH_RATE_TRAIT1_UNSET,
    DEATH_RATE_TRAIT1_SET,
    DEATH_RATE_TRAIT1_UNSET,
)
from src.simulations.scenarios.fbd_no_traits import BIRTH_RATES, DEATH_RATES
from src.utils import set_plt_rcparams


def main():
    output_dir = os.path.join(cfg.FIGURES_DIR, "scenarios")
    os.makedirs(output_dir, exist_ok=True)

    set_plt_rcparams()

    for i, reproduction_number in enumerate(REPRODUCTION_NUMBERS, start=1):
        step(reproduction_number, color="k")
        plt.ylabel("Reproduction number")
        plt.savefig(os.path.join(output_dir, f"epi-skyline_{i}.svg"))
        plt.close()

    sort_idx = np.argsort(MIGRATION_PREDICTOR.flatten())
    plt.plot(
        MIGRATION_PREDICTOR.flatten()[sort_idx],
        MIGRATION_RATES.flatten()[sort_idx],
        marker="o",
        color="k",
    )
    plt.xlabel("Migration predictor")
    plt.ylabel("Migration rate")
    plt.savefig(os.path.join(output_dir, "epi-multitype.svg"))
    plt.close()

    for i, (birth_rate, death_rate) in enumerate(
        zip(BIRTH_RATES, DEATH_RATES), start=1
    ):
        step(birth_rate, label=r"$\lambda$", reverse_xticks=True)
        step(death_rate, label=r"$\mu$", reverse_xticks=True)
        plt.ylabel("Rate")
        plt.legend()
        plt.savefig(os.path.join(output_dir, f"fbd-no-traits_{i}.svg"))
        plt.close()

    step(
        BIRTH_RATE_TRAIT1_UNSET,
        label=r"$\lambda_{0,0} = \lambda_{0,1}$",
        color="C0",
        reverse_xticks=True,
    )
    step(
        BIRTH_RATE_TRAIT1_SET,
        label=r"$\lambda_{1,0} = \lambda_{1,1}$",
        color="C0",
        linestyle="dashed",
        reverse_xticks=True,
    )
    step(
        DEATH_RATE_TRAIT1_UNSET,
        label=r"$\mu_{0,0} = \mu_{0,1}$",
        color="C1",
        reverse_xticks=True,
    )
    step(
        DEATH_RATE_TRAIT1_SET,
        label=r"$\mu_{1,0} = \mu_{1,1}$",
        color="C1",
        linestyle="dashed",
        reverse_xticks=True,
    )
    plt.ylabel("Rate")
    plt.legend()
    plt.savefig(os.path.join(output_dir, "fbd-2traits.svg"))
    plt.close()


if __name__ == "__main__":
    main()
