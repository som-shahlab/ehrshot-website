#!/usr/bin/env python3
"""
Add a new model's results to the EHRSHOT leaderboard.

Usage:
    python scripts/add_model.py results/my_new_model.csv

The CSV should follow the template in results/TEMPLATE.csv.
See results/README.md for full instructions.
"""

import argparse
import csv
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
LEADERBOARD_PATH = os.path.join(ROOT_DIR, "static", "data", "leaderboard.json")

K_VALUES = [1, 2, 4, 8, 12, 16, 24, 32, 48, 64, 128]

TASK_GROUPS = {
    "Operational Outcomes": ["ICU Admission", "Long LOS", "30-day Readmission"],
    "Anticipating Lab Test Results": ["Anemia", "Hyponatremia", "Thrombocytopenia", "Hyperkalemia", "Hypoglycemia"],
    "Assignment of New Diagnoses": ["Acute MI", "Lupus", "Hyperlipidemia", "Hypertension", "Celiac", "Pancreatic Cancer"],
    "Chest X-ray Findings": [
        "Lung Opacity", "Pleural Effusion", "Consolidation", "Pleural Other",
        "Pneumothorax", "Edema", "Enlarged Cardiomediastinum", "Cardiomegaly",
        "Support Devices", "Fracture", "Pneumonia", "Lung Lesion", "Atelectasis", "No Finding",
    ],
}

TASK_TO_GROUP = {}
for group, tasks in TASK_GROUPS.items():
    for task in tasks:
        TASK_TO_GROUP[task] = group

ALL_TASKS = [task for tasks in TASK_GROUPS.values() for task in tasks]


def load_leaderboard():
    with open(LEADERBOARD_PATH, "r") as f:
        return json.load(f)


def save_leaderboard(data):
    with open(LEADERBOARD_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {LEADERBOARD_PATH}")


def parse_csv(csv_path):
    """
    Parse a model results CSV. Expected columns:

    model, metric, task, all, all_ci_low, all_ci_high, all_std,
    k_1, k_2, k_4, k_8, k_12, k_16, k_24, k_32, k_48, k_64, k_128,
    k_1_std, k_2_std, ..., k_128_std

    Returns a dict: {model_name: str, rows: [...]}
    """
    rows = []
    model_name = None

    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)

        # Normalize header names (strip whitespace, lowercase)
        if reader.fieldnames:
            reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]

        for row in reader:
            row = {k.strip().lower(): v.strip() for k, v in row.items()}

            if not row.get("model") or not row.get("metric") or not row.get("task"):
                continue

            if model_name is None:
                model_name = row["model"]
            elif row["model"] != model_name:
                print(f"WARNING: Multiple model names in CSV ({model_name}, {row['model']}). Using first: {model_name}")

            rows.append(row)

    if not model_name:
        print(f"ERROR: No valid rows found in {csv_path}")
        sys.exit(1)

    return {"model_name": model_name, "rows": rows}


def safe_float(val):
    """Convert to float or return None."""
    if val is None:
        return None
    val = str(val).strip()
    if not val or val == "-" or val.lower() == "nan" or val.lower() == "na":
        return None
    try:
        return float(val)
    except ValueError:
        return None


def merge_individual(leaderboard, model_name, rows):
    """Merge per-task (individual) results into the leaderboard."""
    for row in rows:
        metric = row["metric"].lower().strip()
        task = row["task"].strip()

        if metric not in ("auroc", "auprc"):
            print(f"  WARNING: Unknown metric '{metric}' for task '{task}', skipping")
            continue

        if task not in TASK_TO_GROUP:
            print(f"  WARNING: Unknown task '{task}', skipping")
            continue

        individual = leaderboard["individual"]
        if metric not in individual:
            individual[metric] = {}
        if task not in individual[metric]:
            individual[metric][task] = {}

        all_val = safe_float(row.get("all"))
        all_std = safe_float(row.get("all_std"))

        k_scores = {}
        for kv in K_VALUES:
            mean = safe_float(row.get(f"k_{kv}"))
            std = safe_float(row.get(f"k_{kv}_std"))
            if mean is not None:
                entry = {"mean": mean, "std": std if std is not None else 0.0}
                k_scores[str(kv)] = entry

        entry = {
            "all": all_val if all_val is not None else 0.0,
            "allStd": all_std if all_std is not None else 0.0,
            "k": k_scores,
        }

        individual[metric][task][model_name] = entry


def compute_grouped(leaderboard, model_name):
    """
    Compute grouped (by task group) results by averaging per-task results.
    Also computes CI from the 'all' column if all_ci_low / all_ci_high are present.
    """
    individual = leaderboard["individual"]
    grouped = leaderboard["grouped"]

    for metric in ("auroc", "auprc"):
        if metric not in individual:
            continue
        if metric not in grouped:
            grouped[metric] = {}

        for group_name, tasks in TASK_GROUPS.items():
            task_entries = []
            for task in tasks:
                if task in individual.get(metric, {}) and model_name in individual[metric][task]:
                    task_entries.append(individual[metric][task][model_name])

            if not task_entries:
                continue

            if group_name not in grouped[metric]:
                grouped[metric][group_name] = {}

            # Average 'all' across tasks
            all_vals = [e["all"] for e in task_entries if e["all"] is not None]
            avg_all = sum(all_vals) / len(all_vals) if all_vals else 0.0

            # Average k scores across tasks
            avg_k = {}
            for kv in K_VALUES:
                k_str = str(kv)
                means = [e["k"][k_str]["mean"] for e in task_entries if k_str in e["k"]]
                if means:
                    avg_k[k_str] = round(sum(means) / len(means), 3)

            grouped[metric][group_name][model_name] = {
                "all": f"{avg_all:.3f}",
                "k": avg_k,
            }


def merge_grouped_overrides(leaderboard, model_name, rows):
    """
    If the CSV contains rows with task names matching a task group name
    (e.g., "Operational Outcomes"), use those as explicit grouped overrides
    instead of computing from individual tasks. This handles models like MOTOR
    that only have group-level results with CI.
    """
    grouped = leaderboard["grouped"]
    group_names = set(TASK_GROUPS.keys())

    for row in rows:
        task = row["task"].strip()
        if task not in group_names:
            continue

        metric = row["metric"].lower().strip()
        if metric not in ("auroc", "auprc"):
            continue

        if metric not in grouped:
            grouped[metric] = {}
        if task not in grouped[metric]:
            grouped[metric][task] = {}

        all_val = safe_float(row.get("all"))
        ci_low = safe_float(row.get("all_ci_low"))
        ci_high = safe_float(row.get("all_ci_high"))

        k_scores = {}
        for kv in K_VALUES:
            val = safe_float(row.get(f"k_{kv}"))
            if val is not None:
                k_scores[str(kv)] = val

        entry = {
            "all": f"{all_val:.3f}" if all_val is not None else "0.000",
            "k": k_scores,
        }

        if ci_low is not None and ci_high is not None:
            entry["ci"] = f"{ci_low:.3f} - {ci_high:.3f}"

        grouped[metric][task][model_name] = entry


def add_model(csv_path):
    print(f"Loading leaderboard from {LEADERBOARD_PATH}")
    leaderboard = load_leaderboard()

    print(f"Parsing {csv_path}")
    parsed = parse_csv(csv_path)
    model_name = parsed["model_name"]
    rows = parsed["rows"]

    print(f"Model: {model_name}")
    print(f"Rows: {len(rows)}")

    # Check if model already exists
    if model_name in leaderboard["models"]:
        print(f"  Model '{model_name}' already in leaderboard — updating results")
    else:
        leaderboard["models"].append(model_name)
        print(f"  Added '{model_name}' to models list")

    # Separate individual task rows from group-level rows
    group_names = set(TASK_GROUPS.keys())
    individual_rows = [r for r in rows if r["task"].strip() not in group_names]
    group_rows = [r for r in rows if r["task"].strip() in group_names]

    # Merge individual results
    if individual_rows:
        merge_individual(leaderboard, model_name, individual_rows)
        metric_tasks = {}
        for r in individual_rows:
            key = r["metric"].lower()
            metric_tasks.setdefault(key, []).append(r["task"])
        for metric, tasks in metric_tasks.items():
            print(f"  {metric.upper()}: {len(tasks)} individual tasks")

    # Compute grouped from individual (averages)
    if individual_rows:
        compute_grouped(leaderboard, model_name)
        print(f"  Computed grouped averages from individual results")

    # Override grouped with explicit values if provided
    if group_rows:
        merge_grouped_overrides(leaderboard, model_name, group_rows)
        print(f"  Applied {len(group_rows)} explicit grouped overrides (with CI)")

    save_leaderboard(leaderboard)
    print("Done!")


def main():
    parser = argparse.ArgumentParser(description="Add a model's results to the EHRSHOT leaderboard")
    parser.add_argument("csv", help="Path to the model results CSV file")
    args = parser.parse_args()
    add_model(args.csv)


if __name__ == "__main__":
    main()
