#!/usr/bin/env python3
"""
Parse leaderboard HTML tables from the EHRSHOT paper markdown file
and output structured JSON.
"""

import json
import os
import re
from html.parser import HTMLParser


class TableParser(HTMLParser):
    """Parse a single HTML table into a list of rows, each row a list of cell strings."""

    def __init__(self):
        super().__init__()
        self.rows = []
        self._current_row = None
        self._current_cell = None
        self._in_cell = False

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._current_row = []
        elif tag in ("td", "th"):
            self._current_cell = ""
            self._in_cell = True

    def handle_endtag(self, tag):
        if tag == "tr":
            if self._current_row is not None:
                self.rows.append(self._current_row)
            self._current_row = None
        elif tag in ("td", "th"):
            if self._current_row is not None and self._current_cell is not None:
                self._current_row.append(self._current_cell.strip())
            self._current_cell = None
            self._in_cell = False

    def handle_data(self, data):
        if self._in_cell and self._current_cell is not None:
            self._current_cell += data


def parse_table_html(html_str):
    """Parse an HTML table string and return list of data rows (skipping 2 header rows)."""
    parser = TableParser()
    parser.feed(html_str)
    data_rows = []
    for i, row in enumerate(parser.rows):
        if i < 2:
            continue
        data_rows.append(row)
    return data_rows


def parse_grouped_value(val):
    """
    Parse a grouped 'All' value like '0.824 (0.803 - 0.845)'.
    Returns (all_str, ci_str).
    """
    val = val.strip()
    m = re.match(r'([\d.]+)\s*\(([^)]+)\)', val)
    if m:
        return m.group(1), m.group(2).strip()
    return val, None


def parse_individual_value(val):
    """
    Parse an individual value like '0.848 ± 0.0'.
    Returns (mean_float, std_float).
    """
    val = val.strip()
    if not val:
        return None, None
    if "\u00b1" in val:
        parts = val.split("\u00b1")
        mean = float(parts[0].strip())
        std = float(parts[1].strip())
        return mean, std
    try:
        return float(val), None
    except ValueError:
        return None, None


K_VALUES = [1, 2, 4, 8, 12, 16, 24, 32, 48, 64, 128]


def parse_grouped_table(html_str):
    """Parse a grouped (By Task Group) table."""
    rows = parse_table_html(html_str)
    result = {}
    for row in rows:
        if len(row) < 2:
            continue
        model = row[0].strip()
        all_val, ci = parse_grouped_value(row[1])
        k_scores = {}
        for i, kv in enumerate(K_VALUES):
            idx = i + 2
            if idx < len(row) and row[idx].strip():
                try:
                    k_scores[str(kv)] = float(row[idx].strip())
                except ValueError:
                    pass
        entry = {"all": all_val, "k": k_scores}
        if ci is not None:
            entry["ci"] = ci
        result[model] = entry
    return result


def parse_individual_table(html_str):
    """Parse an individual task table."""
    rows = parse_table_html(html_str)
    result = {}
    for row in rows:
        if len(row) < 2:
            continue
        model = row[0].strip()
        all_mean, all_std = parse_individual_value(row[1])
        k_scores = {}
        for i, kv in enumerate(K_VALUES):
            idx = i + 2
            if idx < len(row) and row[idx].strip():
                mean, std = parse_individual_value(row[idx])
                if mean is not None:
                    k_scores[str(kv)] = {"mean": mean, "std": std}
        result[model] = {
            "all": all_mean,
            "allStd": all_std,
            "k": k_scores,
        }
    return result


def extract_tables(content):
    """
    Extract all leaderboard tables from the markdown content, handling
    multi-line tables. Returns list of dicts with section context and HTML.
    """
    # First, find all <table ...leaderboard_table...>...</table> blocks,
    # which may span multiple lines.
    table_pattern = re.compile(
        r'<table[^>]*class="[^"]*leaderboard_table[^"]*"[^>]*>.*?</table>',
        re.DOTALL
    )
    all_tables = list(table_pattern.finditer(content))

    # For each table, determine the section context by looking at
    # the content *before* the table's start position.
    results = []
    for match in all_tables:
        start = match.start()
        preceding = content[:start]
        html = match.group(0)

        # Determine section: grouped or individual
        last_grouped = preceding.rfind('### By Task Group')
        last_individual = preceding.rfind('### Individual')
        if last_individual > last_grouped:
            section = 'individual'
        else:
            section = 'grouped'

        # Determine metric
        last_auroc = preceding.rfind('#### AUROC')
        last_auprc = preceding.rfind('#### AUPRC')
        if last_auprc > last_auroc:
            metric = 'auprc'
        else:
            metric = 'auroc'

        # Determine task group (##### header for individual section)
        task_group = None
        if section == 'individual':
            for m in re.finditer(r'^#{5}\s+(.+)$', preceding, re.MULTILINE):
                task_group = m.group(1).strip()

        # Determine h5 heading (task name for individual, group name for grouped)
        last_h5 = None
        for m in re.finditer(r'<h5>(.+?)</h5>', preceding):
            last_h5 = m.group(1).strip()

        if section == 'grouped':
            group_name = last_h5
            task_name = None
        else:
            group_name = task_group
            task_name = last_h5

        results.append({
            'section': section,
            'metric': metric,
            'taskGroup': group_name,
            'taskName': task_name,
            'html': html,
        })

    return results


def main():
    md_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'content', 'leaderboard', 'paper', 'index.md'
    )
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'static', 'data', 'leaderboard.json'
    )

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    tables = extract_tables(content)

    task_groups = {
        "Operational Outcomes": ["ICU Admission", "Long LOS", "30-day Readmission"],
        "Anticipating Lab Test Results": ["Anemia", "Hyponatremia", "Thrombocytopenia", "Hyperkalemia", "Hypoglycemia"],
        "Assignment of New Diagnoses": ["Acute MI", "Lupus", "Hyperlipidemia", "Hypertension", "Celiac", "Pancreatic Cancer"],
        "Chest X-ray Findings": [
            "Lung Opacity", "Pleural Effusion", "Consolidation", "Pleural Other",
            "Pneumothorax", "Edema", "Enlarged Cardiomediastinum", "Cardiomegaly",
            "Support Devices", "Fracture", "Pneumonia", "Lung Lesion", "Atelectasis", "No Finding"
        ],
    }

    models = ["CLMBR", "GBM", "Logistic Regression", "Random Forest", "MOTOR"]

    grouped = {"auroc": {}, "auprc": {}}
    individual = {"auroc": {}, "auprc": {}}

    for t in tables:
        section = t['section']
        metric = t['metric']
        if section == 'grouped':
            group_name = t['taskGroup']
            data = parse_grouped_table(t['html'])
            grouped[metric][group_name] = data
        elif section == 'individual':
            task_name = t['taskName']
            data = parse_individual_table(t['html'])
            individual[metric][task_name] = data

    output = {
        "models": models,
        "kValues": K_VALUES,
        "taskGroups": task_groups,
        "grouped": grouped,
        "individual": individual,
    }

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    # Print summary
    print(f"Output written to: {out_path}")
    print(f"\nGrouped tables ({len(grouped['auroc']) + len(grouped['auprc'])} total):")
    for metric in ["auroc", "auprc"]:
        for group in grouped[metric]:
            n_models = len(grouped[metric][group])
            print(f"  {metric.upper()} / {group}: {n_models} models")
    print(f"\nIndividual tables ({len(individual['auroc']) + len(individual['auprc'])} total):")
    for metric in ["auroc", "auprc"]:
        for task in individual[metric]:
            n_models = len(individual[metric][task])
            print(f"  {metric.upper()} / {task}: {n_models} models")

    # Validate completeness
    expected_grouped = 8  # 4 groups x 2 metrics
    expected_individual = 56  # 28 tasks x 2 metrics (but some groups have fewer)
    actual_grouped = len(grouped['auroc']) + len(grouped['auprc'])
    actual_individual = len(individual['auroc']) + len(individual['auprc'])
    print(f"\nExpected grouped: {expected_grouped}, got: {actual_grouped}")
    print(f"Expected individual: 56, got: {actual_individual}")
    if actual_grouped != expected_grouped:
        print("WARNING: Missing grouped tables!")
    if actual_individual != 56:
        print("WARNING: Missing individual tables!")


if __name__ == '__main__':
    main()
