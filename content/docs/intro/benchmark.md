---
title: "Benchmark"
description: ""
summary: ""
date: 2023-09-07T16:06:50+02:00
lastmod: 2023-09-07T16:06:50+02:00
draft: false
weight: 800
toc: true
seo:
  title: "" # custom title (optional)
  description: "" # custom description (recommended)
  canonical: "" # custom canonical URL (optional)
  noindex: false # false (default) or true
---

EHRSHOT contains 15 clinical prediction tasks. All tasks are binary classification.

### Tasks

#### Operational Outcomes

These tasks are related to hospital operations. They are defined as follows:

1. **Long Length of Stay:** Predict whether a patient’s total length of stay during a visit to the hospital will be at least 7 days. The prediction time is at 11:59pm on the day of admission, and visits that last less than one day (i.e. discharge occurs on the same day of admission) are ignored.
2. **30-day Readmission:** Predict whether a patient will be re-admitted to the hospital within 30 days after being discharged from a visit. The prediction time is at 11:59pm on the day of admission, and admissions where a readmission occurs on the same day as the corresponding discharge are ignored.
3. **ICU Transfer:** Predict whether a patient will be transferred to the ICU during a visit to the hospital. The prediction time is at 11:59pm on the day of admission, and ICU transfers that occur on the same day as admission are ignored.

#### Anticipating Lab Test Results

These tasks are related to lab value prediction. While we treat these tasks as binary classification tasks in our benchmark (where a label is "negative" if the lab result is normal and "positive" otherwise), we provide multiclass labels (i.e. normal, mild, moderate, severe) for completeness. The prediction time is immediately before the lab result is recorded. They are defined as follows:

1. **Thrombocytopenia:** Predict whether a thrombocytopenia lab comes back as normal (>=150 109/L), mild (>=100 and <150 109/L), moderate (>=50 and <100 109/L), or severe (<50 109/L),. We consider all lab results coded as LOINC/LP393218-5, LOINC/LG32892-8, or LOINC/777-3.
2. **Hyperkalemia:** Predict whether a hyperkalemia lab comes back as normal (<=5.5 mmol/L), mild (>5.5 and <=6mmol/L), moderate (>6 and <=7 mmol/L), or severe (>7 mmol/L). We consider all lab results coded as LOINC LG7931-1, LOINC/LP386618-5, LOINC/LG109906, LOINC/6298-4, or LOINC/2823-3.
3. **Hypoglycemia:** Predict whether a hypoglycemia lab comes back as normal (>=3.9 mmol/L), mild (>=3.5 and <3.9 mmol/L), moderate (>=3 and <3.5 mmol/L), or severe (<3 mmol/L). We consider all lab results coded as SNOMED/33747003, LOINC/LP4161453, or LOINC/14749-6.
4. **Hyponatremia:** Predict whether a hyponatremia lab comes back as normal (>=135 mmol/L), mild (>=130 and <135 mmol/L), moderate (>=125 and <130 mmol/L), or severe (<125 mmol/L). We consider all lab results coded as LOINC/LG11363-5, LOINC/2951-2, or LOINC/2947-0.
5. **Anemia:** Predict whether an anemia lab comes back as normal (>=120 g/L), mild (>=110 and <120 g/L), moderate (>=70 and <110 g/L), or severe (<70 g/L). We consider all lab results coded as LOINC/LP392452-1.

#### Assignment of New Diagnoses

These tasks are related to predicting the first diagnosis of a disease. The prediction time is at 11:59pm on the day of discharge from an inpatient visit, and we count any diagnosis that occurs within 365 days post-discharge as a positive outcome. We ignore all discharges in which the patient already has an existing diagnosis of a disease. The tasks are defined as follows:

1. **Acute MI:** Predict whether the patient will have her first diagnosis of acute myocardial infarction within the next year. We define hypertension as an occurrence of the code SNOMED/57054005, as well as its children codes in our ontology.
1. **Hypertension:** Predict whether the patient will have her first diagnosis of essential hypertension within the next year. We define hypertension as an occurrence of the code SNOMED/59621000, as well as its children codes in our ontology.
2. **Hyperlipidemia:** Predict whether the patient will have her first diagnosis of hyperlipidemia within the next year. We define hyperlipidemia as an occurrence of the code SNOMED/55822004, as well as its children codes in our ontology.
3. **Pancreatic Cancer:** Predict whether the patient will have her first diagnosis of pancreatic cancer within the next year. We define pancreatic cancer as an occurrence of the code SNOMED/372003004, as well as its children codes in our ontology.
4. **Celiac:** Predict whether the patient will have her first diagnosis of celiac disease within the next year. We define celiac disease as an occurrence of the code SNOMED/396331005, as well as its children codes in our ontology.
5. **Lupus:** Predict whether the patient will have her first diagnosis of lupus within the next year. We define lupus as an occurrence of the code SNOMED/55464009, as well as its children codes in our ontology.

#### Anticipating Chest X-ray Findings. 

The chest X-ray findings task requires identifying which of 14 possible findings were included in a chest X-ray report. 

While we treat this task as a binary classification task in our benchmark (where a label is "negative" if the X-ray finding is "No Finding" and "positive" otherwise), we provide multilabel labels (i.e. "No Finding", "Enlarged Cardiomediastinum", "Cardiomegaly", "Lung Lesion", "Lung Opacity", "Edema", "Consolidation", "Pneumonia", "Atelectasis", "Pneumothorax", "Pleural Effusion", "Pleural Other", "Fracture", "Support Devices") for completeness. The prediction time is 24 hours before the radiology report is recorded. The labels are derived by running the CheXpert NLP labeler on the unstructured text of the corresponding radiology report. We do not release this unstructured text as part of our dataset due to patient privacy concerns.

### Label Counts

This is the total number of patients and labels for each task in the benchmark across all splits. Note that the number of labels is greater than the number of patients because each patient can have multiple labels.

| Task Name            | # Total Patients | # Positive Patients | # Negative Patients | Total Labels | # Positive Labels | # Negative Labels | Label Prevalence |
|:-------------------|-------------:|----------------------:|----------------------:|-----------:|--------------------:|--------------------:|-------------------:|
| Long LOS           |         3855 |                  1271 |                  2584 |       6995 |                1767 |                5228 |          0.252609  |
| 30-Day Readmission |         3718 |                   474 |                  3244 |       7003 |                 911 |                6092 |          0.130087  |
| ICU Admission      |         3617 |                   266 |                  3351 |       6491 |                 290 |                6201 |          0.0446772 |
| Thrombocytopenia   |         6063 |                  2566 |                  3497 |     179618 |               59718 |              119900 |          0.332472  |
| Hyperkalemia       |         5931 |                  1289 |                  4642 |     200170 |                4769 |              195401 |          0.0238247 |
| Hypoglycemia       |         5974 |                  1379 |                  4595 |     318164 |                4721 |              313443 |          0.0148383 |
| Hyponatremia       |         5921 |                  3692 |                  2229 |     212837 |               60708 |              152129 |          0.285232  |
| Anemia             |         6086 |                  4271 |                  1815 |     184880 |              127496 |               57384 |          0.689615  |
| Hypertension       |         2328 |                   386 |                  1942 |       3764 |                 516 |                3248 |          0.137088  |
| Hyperlipidemia     |         2650 |                   410 |                  2240 |       4442 |                 566 |                3876 |          0.12742   |
| Pancreatic Cancer  |         3864 |                   214 |                  3650 |       7011 |                 264 |                6747 |          0.0376551 |
| Celiac             |         3899 |                    69 |                  3830 |       7129 |                  94 |                7035 |          0.0131856 |
| Lupus              |         3864 |                   122 |                  3742 |       7038 |                 157 |                6881 |          0.0223075 |
| Acute MI           |         3834 |                   357 |                  3477 |       6837 |                 464 |                6373 |          0.067866  |
| Chest X-Ray        |         1045 |                   996 |                    49 |      26275 |               17203 |                9072 |          0.654729   |

Please note that these numbers are slightly different from the numbers in the paper as the dataset was slightly altered in preparation for public release.

### Access

Please find the benchmark on Redivis, and the code to execute the benchmark on Github here:

* [Dataset + Benchmark](https://redivis.com/datasets/53gc-8rhx41kgt)
* [Code](https://github.com/som-shahlab/ehrshot-benchmark/) 

### Additional Details

For more information, please read [the original EHRSHOT paper](https://arxiv.org/abs/2307.02028).

### Questions?

For questions and feedback, please open an [Issue on Github](https://github.com/som-shahlab/ehrshot-benchmark/)