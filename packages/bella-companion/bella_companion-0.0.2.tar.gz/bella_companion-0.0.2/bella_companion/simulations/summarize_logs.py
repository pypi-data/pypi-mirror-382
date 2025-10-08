import json
import os
from pathlib import Path

import joblib

from bella_companion.simulations.scenarios import SCENARIOS
from bella_companion.utils import summarize_logs as _summarize_logs
from bella_companion.utils import summarize_weights


def summarize_logs():
    output_dir = Path(os.environ["BELLA_BEAST_OUTPUT_DIR"])
    with open(output_dir / "simulations_job_ids.json", "r") as f:
        job_ids: dict[str, dict[str, dict[str, str]]] = json.load(f)

    for scenario_name, scenario in SCENARIOS.items():
        summaries_dir = Path(os.environ["BEAST_LOGS_SUMMARIES_DIR"]) / scenario_name
        os.makedirs(summaries_dir, exist_ok=True)
        for model in job_ids[scenario_name]:
            logs_dir = output_dir / scenario_name / model
            print(f"Summarizing {scenario_name} - {model}")
            summary = _summarize_logs(
                logs_dir,
                target_columns=[c for t in scenario.targets.values() for c in t],
                job_ids=job_ids[scenario_name][model],
            )
            summary.write_csv(summaries_dir / f"{model}.csv")
            if model.startswith("MLP"):
                weights = summarize_weights(logs_dir)
                joblib.dump(weights, summaries_dir / f"{model}.weights.pkl")
