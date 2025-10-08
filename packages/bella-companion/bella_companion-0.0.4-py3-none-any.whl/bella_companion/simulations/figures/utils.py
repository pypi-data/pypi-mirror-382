import os
from itertools import product
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import seaborn as sns
from joblib import Parallel, delayed
from lumiere.backend import (
    ActivationFunction,
    get_partial_dependence_values,
    get_shap_features_importance,
    sigmoid,
)
from lumiere.backend.typings import Weights
from tqdm import tqdm

from src.simulations.features import Feature


def _set_xticks(n: int, reverse: bool = False):
    xticks_labels = range(n)
    if reverse:
        xticks_labels = reversed(xticks_labels)
    plt.xticks(ticks=range(n), labels=list(map(str, xticks_labels)))


def step(
    x: list[float],
    reverse_xticks: bool = False,
    **kwargs: dict[str, Any],
):
    data = x.copy()
    data.insert(0, data[0])
    plt.step(list(range(len(data))), data, **kwargs)
    _set_xticks(len(data), reverse_xticks)
    plt.xlabel("Time bin")


def _count_time_bins(true_values: dict[str, list[float]]) -> int:
    assert (
        len({len(true_value) for true_value in true_values.values()}) == 1
    ), "All targets must have the same number of change times."
    return len(next(iter((true_values.values()))))


def plot_maes_per_time_bin(
    logs_summaries: dict[str, pl.DataFrame],
    true_values: dict[str, list[float]],
    output_filepath: str,
    reverse_xticks: bool = False,
):
    def _mae(target: str, i: int) -> pl.Expr:
        return (pl.col(f"{target}i{i}_median") - true_values[target][i]).abs()

    n_time_bins = _count_time_bins(true_values)
    df = pl.concat(
        logs_summaries[model]
        .select(
            pl.mean_horizontal([_mae(target, i) for target in true_values]).alias("MAE")
        )
        .with_columns(pl.lit(i).alias("Time bin"), pl.lit(model).alias("Model"))
        for i in range(n_time_bins)
        for model in logs_summaries
    )
    sns.violinplot(
        x="Time bin",
        y="MAE",
        hue="Model",
        data=df,
        inner=None,
        cut=0,
        density_norm="width",
        legend=False,
    )
    _set_xticks(n_time_bins, reverse_xticks)
    plt.savefig(output_filepath)
    plt.close()


def plot_coverage_per_time_bin(
    logs_summaries: dict[str, pl.DataFrame],
    true_values: dict[str, list[float]],
    output_filepath: str,
    reverse_xticks: bool = False,
):
    def _coverage(model: str, target: str, i: int) -> float:
        lower_bound = logs_summaries[model][f"{target}i{i}_lower"]
        upper_bound = logs_summaries[model][f"{target}i{i}_upper"]
        true_value = true_values[target][i]
        N = len(logs_summaries[model])
        return ((lower_bound <= true_value) & (true_value <= upper_bound)).sum() / N

    n_time_bins = _count_time_bins(true_values)
    for model in logs_summaries:
        avg_coverage_by_time_bin = [
            np.mean([_coverage(model, target, i) for target in true_values])
            for i in range(_count_time_bins(true_values))
        ]
        plt.plot(avg_coverage_by_time_bin, marker="o")

    _set_xticks(n_time_bins, reverse_xticks)
    plt.xlabel("Time bin")
    plt.ylabel("Coverage")
    plt.ylim((0, 1.05))
    plt.savefig(output_filepath)
    plt.close()


def plot_partial_dependencies(
    weights: list[list[Weights]],  # shape: (n_mcmcs, n_weights_samples, ...)
    features: dict[str, Feature],
    output_dir: str,
    hidden_activation: ActivationFunction = sigmoid,
    output_activation: ActivationFunction = sigmoid,
):
    os.makedirs(output_dir, exist_ok=True)
    features_grid = [feature.grid for feature in features.values()]

    def _get_median_partial_dependence_values(
        weights: list[Weights],
    ) -> list[list[float]]:
        pdvalues_distribution = [
            get_partial_dependence_values(
                weights=w,
                features_grid=features_grid,
                hidden_activation=hidden_activation,
                output_activation=output_activation,
            )
            for w in weights
        ]
        return [
            np.median(
                [pdvalues[feature_idx] for pdvalues in pdvalues_distribution], axis=0
            ).tolist()
            for feature_idx in range(len(features))
        ]

    jobs = Parallel(n_jobs=-1)(
        delayed(_get_median_partial_dependence_values)(w) for w in weights
    )
    pdvalues = [
        job for job in tqdm(jobs, total=len(weights), desc="Evaluating PDPs")
    ]  # shape: (n_mcmcs, n_features, n_grid_points)
    pdvalues = [
        np.array(mcmc_pds).T for mcmc_pds in zip(*pdvalues)
    ]  # shape: (n_features, n_grid_points, n_mcmcs)

    for feature_idx, (feature_name, feature) in enumerate(features.items()):
        color = "red" if feature.is_relevant else "gray"
        feature_pdvalues = pdvalues[feature_idx]  # shape: (n_grid_points, n_mcmcs)
        if not feature.is_categorical:
            median = np.median(feature_pdvalues, axis=1)
            lower = np.percentile(feature_pdvalues, 2.5, axis=1)
            high = np.percentile(feature_pdvalues, 100 - 2.5, axis=1)
            plt.fill_between(feature.grid, lower, high, alpha=0.25, color=color)
            for mcmc_pds in feature_pdvalues.T:
                plt.plot(
                    feature.grid,
                    mcmc_pds,
                    color=color,
                    alpha=0.2,
                    linewidth=1,
                )
            plt.plot(feature.grid, median, color=color, label=feature_name)
    plt.xlabel("Feature value")
    plt.ylabel(f"MLP Output")
    plt.legend()
    plt.savefig(os.path.join(output_dir, "PDPs-continuous.svg"))
    plt.close()

    plot_data = []
    grid_labels = []
    list_labels = []
    for feature_idx, (feature_name, feature) in enumerate(features.items()):
        feature_pdvalues = pdvalues[feature_idx]  # shape: (n_grid_points, n_mcmcs)
        if feature.is_categorical:
            for i, grid_point in enumerate(feature.grid):
                plot_data.extend(feature_pdvalues[i])
                grid_labels.extend([grid_point] * len(feature_pdvalues[i]))
                list_labels.extend([feature_name] * len(feature_pdvalues[i]))
    if not (any(feature.is_categorical for feature in features.values())):
        return
    sns.violinplot(
        x=grid_labels,
        y=plot_data,
        hue=list_labels,
        split=False,
        cut=0,
        palette={
            feature_name: "red" if feature.is_relevant else "gray"
            for feature_name, feature in features.items()
            if feature.is_categorical
        },
    )
    plt.xlabel("Feature value")
    plt.ylabel(f"MLP Output")
    plt.legend()
    plt.savefig(os.path.join(output_dir, "PDPs-categorical.svg"))
    plt.close()


def plot_shap_features_importance(
    weights: list[list[Weights]],  # shape: (n_mcmcs, n_weights_samples, ...)
    features: dict[str, Feature],
    output_file: str,
    hidden_activation: ActivationFunction = sigmoid,
    output_activation: ActivationFunction = sigmoid,
):
    features_grid = [feature.grid for feature in features.values()]
    inputs = list(product(*features_grid))

    def _get_median_shap_features_importance(
        weights: list[Weights],
    ) -> list[list[float]]:
        features_importance = np.array(
            [
                get_shap_features_importance(
                    weights=w,
                    inputs=inputs,
                    hidden_activation=hidden_activation,
                    output_activation=output_activation,
                )
                for w in weights
            ]
        )  # shape: (n_weights_samples, n_features)
        return np.median(features_importance, axis=0).tolist()  # shape: (n_features,)

    jobs = Parallel(n_jobs=-1, return_as="generator_unordered")(
        delayed(_get_median_shap_features_importance)(w) for w in weights
    )
    features_importance_distribution = np.array(
        [job for job in tqdm(jobs, total=len(weights), desc="Evaluating SHAPs")]
    )  # shape: (n_mcmcs, n_features)
    features_importance_distribution /= features_importance_distribution.sum(
        axis=1, keepdims=True
    )

    for i, (feature_name, feature) in enumerate(features.items()):
        sns.violinplot(
            y=features_importance_distribution[:, i],
            x=[feature_name] * features_importance_distribution.shape[0],
            cut=0,
            color="red" if feature.is_relevant else "gray",
        )
    plt.xlabel("Feature")
    plt.ylabel("Importance")
    plt.savefig(output_file)
    plt.close()
