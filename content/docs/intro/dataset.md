---
title: "Dataset"
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

EHRSHOT is a collection of structured data from 6,739 deidentified longitudinal electronic health records (EHRs) sourced from Stanford Medicine.

### Access

* [Dataset + Benchmark](https://redivis.com/datasets/53gc-8rhx41kgt)

### Datasheet

EHRSHOT contains:
* 6,739 patients
* 41,661,637 million clinical events
* 921,499 visits
* 15 prediction tasks

Each patient consists of an ordered timeline of clinical events taken from the structured data of their EHR (e.g. diagnoses, procedures, prescriptions, etc.). Note that EHRSHOT does NOT contain clinical text or images.

### Sample

The raw EHRSHOT dataset is a single CSV with 41M rows that looks like:

| patient_id | start              | end                | code   | value | unit | visit_id    | omop_table    |
|------------|--------------------|--------------------|--------|-------|------|-------------|---------------|
| 12  | 2010-04-08 01:30:00| 2010-04-09 10:33:00| CPT4/86850 |       |      | 4930  | procedure_occurrence |
| 105  | 2001-10-28 16:11:00| 2001-10-28 16:11:00| SNOMED/387458008 |       |      | 940 | drug_exposure |
| ... | ... | ... | ... | ... | ... | ... | ... |

### Format
The EHRSHOT dataset is a single CSV with these columns:
1. `patient_id` - Integer - Unique identifier for patient
2. `start` - Datetime - Start time of event
3. `end` - Datetime (optional) - End time of event
4. `code` - String - Name of the clinical event (e.g. "SNOMED/3950001" or "ICD10/I25.110")
5. `value` - Float/String (optional) - Either a numerical value associated with an event (e.g. a lab test result) or a string associated with a categorical variable (e.g. "Yes/No" questions)
6. `unit` - String (optional) - Unit of measurement for Value
7. `visit_id` - Integer (optional) - Unique identifier for the visit during which this event occurred
8. `omop_table` - String - Name of the source [OMOP-CDM table](https://ohdsi.github.io/CommonDataModel/cdm53.html) where this event was recorded

### Statistics

##### Events

* Events per patient (median): 2592.0
* Events per patient (mean): 6182.2

<img src="/images/dataset_events.png" class="border-0 mt-2">


##### Visits

* Visits per patient (median): 58.0
* Visits per patient (mean): 136.7

<img src="/images/dataset_visits.png" class="border-0 mt-2">


##### Timeline Lengths

Note: The timeline length is the time between the first and last visit for each patient. We exclude patients without any visits.

* Timeline length in years per patient (median): 7.8
* Timeline length in years per patient (mean): 8.6

<img src="/images/dataset_timelines.png" class="border-0 mt-2">

##### Visit Type Counts

Here is the count of each type of visit. Note the higher prevalence of outpatient visits in EHRSHOT.

| Visit Type         | Definition | Count  |
|--------------------|------------|--------|
| Visit/OP           | Outpatient Visit | 184318 |
| Visit/OMOP4822458  | Office Visit | 132597 |
| Visit/IP           | Inpatient Visit | 35748  |
| Visit/OMOP4822461  | Laboratory Visit | 13240  |
| Visit/ER           | Emergency Visit | 9553   |
| Visit/ERIP         | Emergency Room and Inpatient Visit | 4861   |

### Additional Details

For more information, please read [the original EHRSHOT paper](https://arxiv.org/abs/2307.02028).

### Questions?

For questions and feedback, please open an [Issue on Github](https://github.com/som-shahlab/ehrshot-benchmark/)
