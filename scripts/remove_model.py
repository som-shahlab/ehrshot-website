#!/usr/bin/env python3
"""
Remove a model from the EHRSHOT leaderboard.

Usage:
    python scripts/remove_model.py "ModelName"
"""

import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
LEADERBOARD_PATH = os.path.join(ROOT_DIR, "static", "data", "leaderboard.json")


def main():
    parser = argparse.ArgumentParser(description="Remove a model from the EHRSHOT leaderboard")
    parser.add_argument("model", help="Model name to remove (exact match)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed without saving")
    args = parser.parse_args()

    with open(LEADERBOARD_PATH, "r") as f:
        data = json.load(f)

    model = args.model
    if model not in data["models"]:
        print(f"Model '{model}' not found. Available models:")
        for m in data["models"]:
            print(f"  - {m}")
        sys.exit(1)

    removed = 0
    data["models"] = [m for m in data["models"] if m != model]

    for section in ("grouped", "individual"):
        for metric in ("auroc", "auprc"):
            if metric not in data.get(section, {}):
                continue
            for task in data[section][metric]:
                if model in data[section][metric][task]:
                    if not args.dry_run:
                        del data[section][metric][task][model]
                    removed += 1
                    print(f"  {'Would remove' if args.dry_run else 'Removed'}: {section}/{metric}/{task}")

    if args.dry_run:
        print(f"\nDry run: would remove {removed} entries for '{model}'")
    else:
        with open(LEADERBOARD_PATH, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nRemoved {removed} entries for '{model}'")
        print(f"Saved to {LEADERBOARD_PATH}")


if __name__ == "__main__":
    main()
