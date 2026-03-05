# BMIS476MortonAnalytics

# 🚢 DDT — GEN AI AIS Event Detection & Labeling Pipeline

> **GEN AI DATA PROCESSING AND ANALYTICS SOLUTION PROJECT**
> Developed by the DDT Team

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [System Requirements Coverage](#-system-requirements-coverage)
- [Installation](#-installation)
- [How to Run](#-how-to-run)
- [Pipeline Sections](#-pipeline-sections)
- [Output Files](#-output-files)
- [Project Structure](#-project-structure)
- [Notes](#-notes)

---

## 📌 Project Overview

This pipeline reads large AIS (Automatic Identification System) vessel tracking datasets and automatically detects, labels, and summarizes key maritime events. It is designed to handle datasets of **8 million+ rows** efficiently using vectorized processing and chunked file loading.

**Detected Events:**

| Event | Description |
|-------|-------------|
| `ARRIVAL` | Vessel slows to near-stop after moving |
| `DEPARTURE` | Vessel accelerates after being stopped |
| `ANCHORING` | Vessel remains near-stationary for multiple readings |
| `ROUTE_DEVIATION` | Sudden large change in vessel heading |
| `PROXIMITY` | Two vessels within configured distance of each other |

---

## ✅ System Requirements Coverage

A full breakdown of each project requirement, its priority level, and whether it has been implemented in the pipeline.

| Req # | Priority | Description | Status |
|-------|----------|-------------|--------|
| #1 | 🔴 Critical | Event Labeling GenAI System | ✅ Implemented |
| #2 | 🔴 Critical | Identify location of shipments | ✅ Implemented |
| #3 | 🟡 High | Structured Event Data Output | ✅ Implemented |
| #4 | 🟡 High | Event Detection and Labeling | ✅ Implemented |
| #5 | 🟡 High | Event Object Generation | ✅ Implemented |
| #6 | 🟡 High | Data Formatted in New Columns + CSV Export | ✅ Implemented |
| #7 | 🔴 Critical | Documentation | ✅ Implemented |
| #8 | 🟡 High | Data Labeling Output Format (CSV) | ✅ Implemented |
| #9 | 🟡 High | Natural Language AI Event Summary | ✅ Implemented |
| #10 | 🟡 High | System Compatibility (CSV, JSON, NMEA) | ✅ Implemented |

---

## 💻 Installation

Follow these steps to get the project set up on your machine for the first time.

**1. Clone the repository**
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

**2. Install dependencies**
```bash
pip install pandas numpy anthropic pyais tqdm
```

> `tkinter` is used for the file browser dialog and comes pre-installed with Python.
> If you get an error, run: `pip install tk`

**3. Set your Anthropic API key** *(only needed for AI summaries — Req #9)*
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

## ▶️ How to Run

There are two ways to run the pipeline — pick whichever fits your workflow.

**Option A — File Browser (Recommended)**

Add these two lines to the bottom of the script and run it:
```python
df = import_dataset()
labeled_df, events_df = run_pipeline_from_df(df)
```
A file picker window will open. Select your `.csv`, `.json`, or `.nmea` file. The full dataset loads into memory only — **it is never saved to your project folder**, keeping your GitHub repo clean.

---

**Option B — Terminal / Command Line**
```bash
# Basic run
python ddt_ais_pipeline.py your_data.csv --output-dir ./output

# With AI summaries (requires API key)
python ddt_ais_pipeline.py your_data.csv --output-dir ./output --ai-summaries

# Limit number of AI summaries generated
python ddt_ais_pipeline.py your_data.csv --output-dir ./output --ai-summaries --max-summaries 100
```

---

## 🔧 Pipeline Sections

### Section 1 — Configuration `CONFIG`
> *Supports all requirements*

The central control panel for the entire pipeline. Stores all adjustable settings in one place — speed thresholds (knots), bearing change thresholds (degrees), proximity distance (nautical miles), chunk size for large file loading, and column name aliases for each required field. All other sections reference this CONFIG dictionary, so you only ever need to change one place to affect the whole pipeline.

---

### Section 2 — Utility Functions
> *Supports all sections*

Small, reusable helper functions called throughout the pipeline. Includes vectorized haversine distance calculation (nautical miles), angular bearing change calculation with 0°/360° wrap-around handling, column name resolver, unique event ID generator, rule-based confidence scorer (0.0–1.0), NULL field checker, and terminal progress formatting.

---

### Section 3 — Data Loaders
> *Req #10 — System Compatibility*

Handles reading raw AIS data from disk in three formats:
- **CSV** — chunked reading (500K rows at a time) with dtype optimization for 8M+ row datasets
- **JSON** — supports standard arrays and newline-delimited JSON (NDJSON)
- **NMEA** — decodes raw AIS radio sentences (VDM/VDO) using `pyais`

File type is auto-detected from extension — no manual format selection needed.

---

### Section 4 — Column Resolution
> *Internal — supports all detection sections*

Automatically maps your dataset's column names to the pipeline's internal field names using the alias lists in Section 1. Required columns (MMSI, latitude, longitude, timestamp) raise a clear error if not found. Optional columns (speed, course, vessel name) return `None` and cause the relevant detection step to be skipped gracefully rather than crashing.

---

### Section 5 — Event Detection Engine ⚙️
> *Req #1, #2, #4, #5 — Core Labeling System*

The primary implementation of the GenAI event labeling requirement. Uses fully vectorized pandas/NumPy operations — **no Python for-loops on the full dataset** — making it capable of processing millions of rows in seconds.

| Detection Type | Method | Events Produced |
|---|---|---|
| Speed-based | `shift()` comparison per vessel | `ARRIVAL`, `DEPARTURE`, `ANCHORING` |
| Course-based | Vectorized bearing delta | `ROUTE_DEVIATION` |
| Cross-vessel | Time-bucketed spatial grouping | `PROXIMITY` |

Every detected event is recorded as a structured object containing: `event_id`, `vessel_id`, `vessel_name`, `event_type`, `timestamp`, `latitude`, `longitude`, `confidence_score`, `null_flags`.

---

### Section 6 — AI Natural Language Summaries
> *Req #9 — Natural Language AI Event Summary*

Uses the Claude API to generate a plain-English sentence for each detected event. A structured prompt containing the event type, vessel details, timestamp, coordinates, and confidence score is sent to the model, and the response is stored in an `ai_summary` column.

- Capped at a configurable limit (default: 500 events) to control cost and runtime
- Rate-limited between calls to avoid API errors
- Skips gracefully if API key is not set or `anthropic` is not installed

---

### Section 7 — Output Builder
> *Req #3, #6, #8 — Structured Output & New Columns*

Merges detected event labels back into the original AIS DataFrame as new columns. Builds a fast lookup dictionary keyed on `(vessel_id, timestamp_minute)` and tags each original row that matches a detected event. Rows with no matching event are left blank in the new columns.

**New columns added to your data:**

| Column | Description |
|--------|-------------|
| `event_id` | Unique identifier e.g. `EVT-3A9F12BC` |
| `event_type` | `ARRIVAL`, `DEPARTURE`, `ANCHORING`, `ROUTE_DEVIATION`, `PROXIMITY` |
| `confidence_score` | Reliability score from `0.0` to `1.0` |
| `null_flags` | Any missing key fields in this row |
| `ai_summary` | Plain-English event description (if enabled) |

---

### Section 8 — CSV Export
> *Req #6, #8 — Final CSV Export Function*

Writes two output files:
- **`labeled_output.csv`** — full original dataset with the 5 new event columns appended
- **`events_summary.csv`** — events-only file, compact and suitable for dashboards or analytics tools

Uses chunked write mode (100K rows per batch) to prevent memory spikes during export on large datasets. Reports file path, row count, and file size after each export.

---

### Section 9 — Pipeline Summary Report
> *Req #7 — Documentation of Processing Pipeline*

Prints a human-readable run summary to the terminal at the end of every pipeline execution. Includes input file name, total rows processed, labeled row count and percentage, output directory, event type breakdown, AI summary status, and total runtime in seconds.

---

### Section 10 — Main Pipeline Orchestrator
> *All Requirements — End-to-End Coordination*

The master coordinator that calls each section in order. Defines two entry points:
- `run_pipeline(filepath)` — loads file then runs full pipeline
- `run_pipeline_from_df(df)` — skips loading, runs pipeline on an already-loaded DataFrame (used with the file browser import)

---

### Section 11 — Command Line Interface (Nessesary for the  )
> *Developer Utility — Terminal Execution*

*Reads that command, understands what you typed, and passes it to the pipeline. Without it, Python wouldn't know what to do with your_data.csv or --output-dir.

Enables the script to be run directly from the terminal using `argparse`. Accepts three arguments: input file path (required), `--output-dir` (optional), and `--ai-summaries` (flag). Used for automated runs, server-side execution, or CI/CD integration. Bypassed when using the file browser import workflow.

---

## 📁 Output Files

After the pipeline runs, two output files are written to the output folder and one small preview file is saved for reference.

```
output/
├── labeled_output.csv        ← Full dataset + event label columns
└── events_summary.csv        ← Events-only summary (one row per event)

preview/
└── your_data_preview.csv     ← First 10 rows only — safe to commit to GitHub
```

> ⚠️ Add the following to your `.gitignore` to keep large files off GitHub:
> ```
> /output/
> *.csv
> !preview/*_preview.csv
> ```

---

## 🗂️ Project Structure

A quick map of what each file and folder in this project is for.

```
your-repo/
├── ddt_ais_pipeline.py       ← Main pipeline script (all 11 sections)
├── import_function.py        ← File browser import + memory-only loading
├── preview/
│   └── *_preview.csv         ← Small sample files (safe to commit)
├── output/                   ← Generated outputs (add to .gitignore)
└── README.md                 ← This file
```

---

## 📝 Notes

A few important things to be aware of when working with this pipeline.

- The full dataset is **never written to your project folder** when using the file browser import — it lives in memory only, keeping your GitHub repo clean and avoiding large file push errors.
- Column names are auto-resolved from aliases — if your dataset uses different names, add them to the `CONFIG` block at the top of `ddt_ais_pipeline.py`.
- AI summaries require an `ANTHROPIC_API_KEY` environment variable and the `anthropic` Python package.
- For NMEA files, `pyais` must be installed: `pip install pyais`

---

*DDT Team — GEN AI DATA PROCESSING AND ANALYTICS SOLUTION PROJECT*