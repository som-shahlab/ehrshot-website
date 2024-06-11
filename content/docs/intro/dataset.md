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

EHRSHOT is a collection of 6,739 deidentified longitudinal electronic health records (EHRs) sourced from Stanford Medicine.

### Access

* [Dataset + Benchmark](https://redivis.com/datasets/53gc-8rhx41kgt)

### Datasheet

EHRSHOT contains:
* 6,739 patients
* 41,661,637 million clinical events
* 921,499 visits
* 15 prediction tasks

Each patient consists of an ordered timeline of clinical events taken from the structured data of their EHR (e.g. diagnoses, procedures, prescriptions, etc.).

### Statistics

##### Events

* Events per patient (median): 2592.0
* Events per patient (mean): 6182.2

<img src="/images/dataset_events.png" class="border-0 mt-2">


##### Visits

* Visits per patient (median): 2592.0
* Visits per patient (mean): 6182.2

<img src="/images/dataset_visits.png" class="border-0 mt-2">


##### Timeline Lengths

Note: The timeline length is the time between the first and last visit for each patient. We exclude patients without any visits.

* Timeline length in years per patient (median): 7.8
* Timeline length in years per patient (mean): 8.6

<img src="/images/dataset_timelines.png" class="border-0 mt-2">

### Additional Details

For more information, please read [the original EHRSHOT paper](https://arxiv.org/abs/2307.02028).

### Questions?

For questions and feedback, please open an [Issue on Github](https://github.com/som-shahlab/ehrshot-benchmark/)