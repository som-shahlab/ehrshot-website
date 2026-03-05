# Adding New Model Results to the EHRSHOT Leaderboard

## Quick Start

1. Copy the template:
   ```bash
   cp results/TEMPLATE.csv results/my_model.csv
   ```

2. Fill in your results (replace `MyModel` with your model name, fill in scores)

3. Run:
   ```bash
   python scripts/add_model.py results/my_model.csv
   ```

4. Rebuild the site:
   ```bash
   hugo server
   ```

That's it. Your model will appear on the leaderboard.

## CSV Format

Each row is one **(model, metric, task)** combination. The CSV has these columns:

| Column | Required | Description |
|--------|----------|-------------|
| `model` | Yes | Model name (e.g., `CLMBR-v2`) |
| `metric` | Yes | `auroc` or `auprc` |
| `task` | Yes | Task name (must match exactly — see list below) |
| `all` | Yes | Score on the full training set |
| `all_ci_low` | No | Lower bound of 95% CI on `all` |
| `all_ci_high` | No | Upper bound of 95% CI on `all` |
| `all_std` | No | Std dev of `all` (across replicates) |
| `k_1` ... `k_128` | No | Mean score at each few-shot k value |
| `k_1_std` ... `k_128_std` | No | Std dev at each k value |

### Task Names (must match exactly)

**Operational Outcomes:** ICU Admission, Long LOS, 30-day Readmission

**Anticipating Lab Test Results:** Anemia, Hyponatremia, Thrombocytopenia, Hyperkalemia, Hypoglycemia

**Assignment of New Diagnoses:** Acute MI, Lupus, Hyperlipidemia, Hypertension, Celiac, Pancreatic Cancer

**Chest X-ray Findings:** Lung Opacity, Pleural Effusion, Consolidation, Pleural Other, Pneumothorax, Edema, Enlarged Cardiomediastinum, Cardiomegaly, Support Devices, Fracture, Pneumonia, Lung Lesion, Atelectasis, No Finding

### k Values

The benchmark uses these few-shot k values: **1, 2, 4, 8, 12, 16, 24, 32, 48, 64, 128**

## Flexibility

- **Partial results are fine.** Leave cells empty if you don't have results for every task or every k. Only tasks with data will appear on the leaderboard.

- **Group-level overrides.** If you only have aggregated results (e.g., averaged across all tasks in "Operational Outcomes"), you can add rows where `task` is the group name instead of the individual task name. The script will use those directly instead of computing averages. Useful if you have group-level confidence intervals.

- **Updating a model.** Running the script again with the same model name will overwrite that model's existing results.

- **Multiple models.** Run the script once per CSV. Each CSV should contain results for a single model.

## Example

A model with only group-level AUROC (like MOTOR):

```csv
model,metric,task,all,all_ci_low,all_ci_high,all_std,k_1,k_2,...
MOTOR-v2,auroc,Operational Outcomes,0.840,0.820,0.860,,,,,...
MOTOR-v2,auroc,Anticipating Lab Test Results,0.795,0.785,0.805,,,,,...
```

A model with full per-task results:

```csv
model,metric,task,all,all_ci_low,all_ci_high,all_std,k_1,k_2,...,k_128,k_1_std,...,k_128_std
NewModel,auroc,ICU Admission,0.860,,,0.005,0.610,0.620,...,0.845,0.08,0.07,...,0.01
NewModel,auroc,Long LOS,0.820,,,0.003,0.540,0.560,...,0.780,0.06,0.05,...,0.01
...
```
