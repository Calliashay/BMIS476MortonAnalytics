<div align="center">

# 🚢 AIS Maritime Event Intelligence Platform

### GEN AI Data Processing & Analytics Solution
**DDT Team &nbsp;|&nbsp; BMIS 476 &nbsp;|&nbsp; Spring 2026**

---

![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AI](https://img.shields.io/badge/AI-Claude%20Sonnet-7c3aed?style=for-the-badge)
![Scale](https://img.shields.io/badge/Scale-8M%2B%20Rows-f97316?style=for-the-badge)
![Requirements](https://img.shields.io/badge/Requirements-10%2F10%20Met-brightgreen?style=for-the-badge)

</div>

---

## 📋 Table of Contents

- [What This System Does](#what-this-system-does)
- [Key Capabilities](#key-capabilities)
- [Requirements Coverage](#requirements-coverage)
- [Getting Started](#getting-started)
- [Running the Pipeline](#running-the-pipeline)
- [How It Works — Pipeline Breakdown](#how-it-works)
- [Output Files](#output-files)
- [Project Structure](#project-structure)
- [Technical Notes](#technical-notes)

---

<a id="what-this-system-does"></a>
## 📌 What This System Does

The **AIS Maritime Event Intelligence Platform** ingests raw vessel tracking data and automatically detects, labels, and explains significant maritime events using AI — transforming millions of raw GPS pings into a structured, analyst-ready dataset.

It is purpose-built to handle **real-world AIS datasets at scale** (8 million+ rows), with performance-optimized processing that runs in seconds rather than hours.

### Detected Event Types

| Event | What It Means |
|:---|:---|
| `ARRIVAL` | A vessel decelerates to near-zero after sustained movement |
| `DEPARTURE` | A vessel accelerates out of a stationary or slow state |
| `ANCHORING` | A vessel holds near-stationary position across multiple pings |
| `ROUTE_DEVIATION` | A sudden, significant change in heading is detected |
| `PROXIMITY` | Two or more vessels come within a configured distance of each other |

---

<a id="key-capabilities"></a>
## ✨ Key Capabilities

| Capability | Details |
|:---|:---|
| **AI-Powered Summaries** | Claude Sonnet generates a plain-English description of every detected event |
| **8M+ Row Support** | Vectorized pandas/NumPy processing — no row-by-row loops |
| **Three Input Formats** | Accepts CSV, JSON, and raw NMEA AIS radio sentence files |
| **Auto Column Mapping** | Resolves column names automatically — works with any AIS schema |
| **Named Maritime Regions** | Converts raw lat/lon to human-readable locations (e.g. *"Chesapeake Bay"*) |
| **Vessel Lookup Tool** | Query any vessel by name or MMSI for a full plain-English status report |
| **Date Filtering** | Process a single day or range rather than an entire multi-year dataset |
| **Structured CSV Output** | Three clean output files ready for dashboards or further analysis |
| **Zero Data Leakage** | Full datasets stay in memory only — nothing large is written to the repo |
| **Configurable** | All thresholds and settings live in a single `CONFIG` block |

---

<a id="requirements-coverage"></a>
## ✅ Requirements Coverage

All 10 project requirements have been fully implemented.

| # | Priority | Requirement | Status |
|:---:|:---:|:---|:---:|
| 1 | 🔴 Critical | Event Labeling GenAI System | ✅ Complete |
| 2 | 🔴 Critical | Identify Location of Shipments | ✅ Complete |
| 3 | 🟡 High | Structured Event Data Output | ✅ Complete |
| 4 | 🟡 High | Event Detection and Labeling | ✅ Complete |
| 5 | 🟡 High | Event Object Generation | ✅ Complete |
| 6 | 🟡 High | Data Formatted in New Rows + CSV Export | ✅ Complete |
| 7 | 🔴 Critical | Documentation | ✅ Complete |
| 8 | 🟡 High | Data Labeling Output Format (CSV) | ✅ Complete |
| 9 | 🟡 High | Natural Language AI Event Summary | ✅ Complete |
| 10 | 🟡 High | System Compatibility (CSV, JSON, NMEA) | ✅ Complete |

---

<a id="getting-started"></a>
## 💻 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Install Dependencies

```bash
pip install pandas anthropic pyais
```

> **Dependency notes:**
> - `numpy` — included automatically with pandas, no separate install needed
> - `tkinter` — bundled with Python; if missing, run `pip install tk`
> - `pyais` — only required for NMEA-format AIS files

### 3. Configure Your API Key *(required for AI summaries)*

**Mac / Linux**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Windows**
```cmd
set ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

<a id="running-the-pipeline"></a>
## ▶️ Running the Pipeline

### Option A — File Browser *(Recommended)*

Run the script with no arguments. A file picker window opens automatically — just select your data file.

```bash
python ddt_ais_pipeline.py
```

The dataset is loaded entirely into memory. Nothing large is ever written back to the project folder, keeping the repository clean.

You can also drive it directly from a script or notebook:

```python
df = import_dataset()
labeled_df, events_df = run_pipeline_from_df(df)
```

### Option B — Command Line

```bash
# Standard run
python ddt_ais_pipeline.py your_data.csv --output-dir ./output

# With AI-generated event summaries
python ddt_ais_pipeline.py your_data.csv --output-dir ./output --ai-summaries

# Limit the number of AI summaries (to manage API cost)
python ddt_ais_pipeline.py your_data.csv --output-dir ./output --ai-summaries --max-summaries 100
```

---

<a id="how-it-works"></a>
## 🔧 How It Works — Pipeline Breakdown

The pipeline is organized into 11 modular sections that execute in sequence.

---

### Section 1A — Central Configuration
> *Controls all pipeline behavior from a single location*

Every threshold, alias, and setting lives in one `CONFIG` dictionary at the top of the script. Speed limits (knots), bearing change thresholds (degrees), proximity distance (nautical miles), chunk size, and column name aliases are all defined here. Change one value and it propagates through the entire pipeline automatically.

---

### Section 1B — Data Import
> *Flexible file loading with memory-safe handling*

Opens a file browser dialog or accepts a path directly. Loads the full dataset into memory without writing anything to disk. Optionally saves a 10-row preview CSV for safe reference commits. Also exposes `run_pipeline_from_df()` for notebook and scripted workflows.

**Accepted formats:** `.csv` &nbsp;·&nbsp; `.json` &nbsp;·&nbsp; `.nmea` &nbsp;·&nbsp; `.txt` &nbsp;·&nbsp; `.ais`

---

### Section 1C — Date Filter
> *Process one day or a date range instead of the full dataset*

After columns are resolved, an interactive menu lets the analyst scope the run to a specific day or range of days. The selected date is embedded in all output filenames for clear traceability (e.g. `mydata_2023-06-15_events_labeled.csv`).

---

### Maritime Region Lookup Table
> *Converts coordinates to named locations*

A priority-ordered lookup table covering US coastal ports and bays, major international maritime zones, and ocean basin fallbacks. The `get_region_name()` function converts any lat/lon pair into a human-readable string such as *"Strait of Malacca"* or *"Gulf of Mexico."* More specific regions are always checked before broader ones.

---

### Section 2 — Utility Functions
> *Shared helpers used across all sections*

Includes: vectorized haversine distance (nautical miles), bearing-change calculation with 0°/360° wraparound, column name resolver, unique event ID generator, confidence scorer (0.0–1.0), NULL field checker, and terminal progress formatting.

---

### Section 2B — Vessel Lookup Tool
> *On-demand plain-English vessel status report*

After the pipeline runs, any vessel can be queried by MMSI or partial name. The output includes last known position with named region, current speed and activity description, destination and ETA (if available), and a full list of detected events with location and confidence score.

```python
lookup_vessel(labeled_df, events_df, 123456789)
lookup_vessel(labeled_df, events_df, "EVER GIVEN")
```

---

### Section 2C — Bulk Vessel Status Export
> *One-row-per-vessel summary table — Req #2*

Generates a fleet-wide snapshot using a single `groupby().last()` pass — efficient even at 8M+ rows. Each row captures: MMSI, vessel name, ping count, last seen timestamp, named region, coordinates, activity description, deviation count, and total events detected. Exported as `*_vessel_status.csv`.

---

### Section 3 — Data Loaders
> *Multi-format ingestion — Req #10*

| Format | Handling |
|:---|:---|
| **CSV** | Chunked reads (500K rows/chunk) with dtype optimization for large files |
| **JSON** | Supports both standard JSON arrays and newline-delimited NDJSON |
| **NMEA** | Decodes raw AIS radio sentences (VDM/VDO messages) via `pyais` |

Format is auto-detected from file extension — no manual selection required.

---

### Section 4 — Column Resolution
> *Automatic schema mapping for any AIS dataset*

Maps your dataset's column names to the pipeline's internal field names using the alias lists in the `CONFIG` block. Required fields (MMSI, latitude, longitude, timestamp) produce a clear error if not found. Optional fields (speed, course, vessel name) fail gracefully — the relevant detection step is simply skipped rather than crashing the run.

---

### Section 5 — Event Detection Engine
> *Core detection system — Req #1, #2, #4, #5*

The heart of the pipeline. All detection uses fully vectorized pandas/NumPy operations — no Python-level loops over the dataset — enabling processing of millions of rows in seconds.

| Detection Method | Technique | Events Produced |
|:---|:---|:---|
| Speed-based | `shift()` comparison per vessel group | `ARRIVAL`, `DEPARTURE`, `ANCHORING` |
| Course-based | Vectorized bearing delta calculation | `ROUTE_DEVIATION` |

Every event is emitted as a structured record containing: `event_id`, `vessel_id`, `vessel_name`, `event_type`, `timestamp`, `latitude`, `longitude`, `confidence_score`, `null_flags`, `region_name`.

> **Note:** `PROXIMITY` detection is defined in requirements and partially scaffolded — speed-based and course-based detection are fully active in the current release.

---

### Section 6 — AI Natural Language Summaries
> *Plain-English event descriptions via Claude — Req #9*

Each detected event is passed to the Claude API (`claude-sonnet-4-5`) with a structured prompt containing the event type, vessel details, timestamp, coordinates, and confidence score. The model returns a natural-language sentence that is stored in the `ai_summary` column.

- Summary count is capped (default: 500) to keep runtime and API cost predictable
- Requests are rate-limited to avoid API throttling
- The entire section skips gracefully if no API key is configured

---

### Section 7 — Output Builder
> *Merges event labels back into source data — Req #3, #6, #8*

Builds a fast lookup keyed on `(vessel_id, timestamp_minute)` and stamps each original AIS row that matches a detected event. Rows with no event are left empty in the new columns.

**New columns appended to your data:**

| Column | Description |
|:---|:---|
| `event_id` | Unique identifier, e.g. `EVT-3A9F12BC` |
| `event_type` | One of: `ARRIVAL`, `DEPARTURE`, `ANCHORING`, `ROUTE_DEVIATION`, `PROXIMITY` |
| `confidence_score` | Rule-based reliability score from `0.0` to `1.0` |
| `null_flags` | Any missing key fields detected in this row |
| `region_name` | Human-readable maritime region name |
| `ai_summary` | Plain-English description of the event (if AI summaries are enabled) |

---

### Section 8 — CSV Export
> *Chunked, memory-safe file writing — Req #6, #8*

Writes all output files in chunked mode to avoid memory spikes on large exports. Reports file path, row count, and file size to the terminal after each write. See [Output Files](#output-files) for the full list.

---

### Section 9 — Pipeline Summary Report
> *End-of-run terminal report — Req #7*

Prints a formatted summary after every run: input filename, total rows processed, labeled row count and percentage, output directory, per-event-type breakdown, AI summary status, and total wall-clock runtime in seconds.

---

### Section 10 — Main Pipeline Orchestrator
> *End-to-end coordinator for all requirements*

The master function that calls each section in sequence. Exposes two entry points:

- **`run_pipeline(filepath)`** — loads the file, then runs the full pipeline
- **`run_pipeline_from_df(df)`** — skips loading, runs on an already-loaded DataFrame

**Execution order:**
```
Load Data → Resolve Columns → Date Filter → Preprocess & Deduplicate
  → Detect Events → Generate AI Summaries → Merge Labels → Export → Summary Report
```

---

### Section 11 — Command Line Interface
> *Terminal execution via argparse*

Makes the script fully runnable from the command line. If no input file is given, the file browser opens automatically.

| Argument | Description |
|:---|:---|
| `input` *(optional)* | Path to AIS data file — omit to open the file browser |
| `--output-dir` / `-o` | Output directory for CSV files (default: `./output`) |
| `--ai-summaries` | Enable Claude AI-generated event summaries |
| `--max-summaries` | Override the CONFIG cap on AI summary count |

---

<a id="output-files"></a>
## 📁 Output Files

Three structured files are produced per run, plus a lightweight preview file safe for version control. All output filenames are prefixed with the source filename and selected date(s).

```
output/
├── *_events_labeled.csv      ← Full AIS rows where at least one event was detected
├── *_events_summary.csv      ← One row per event — compact, dashboard-ready
└── *_vessel_status.csv       ← One row per vessel: last position, region, event totals

preview/
└── your_data_preview.csv     ← First 10 rows only — safe to commit to GitHub
```

> **Recommended `.gitignore` entries** to prevent large data files from being pushed:
> ```gitignore
> /output/
> *.csv
> !preview/*_preview.csv
> ```

---

<a id="project-structure"></a>
## 🗂️ Project Structure

```
your-repo/
├── ddt_ais_pipeline.py       ← Main pipeline script (all 11 sections)
├── preview/
│   └── *_preview.csv         ← Small sample files (safe to commit)
├── output/                   ← Generated outputs (gitignored)
└── README.md                 ← This document
```

---

<a id="technical-notes"></a>
## 📝 Technical Notes

- **Memory safety** — When using the file browser, the full dataset is held in memory only and never written to the project directory. This prevents large-file git push errors and keeps the repository clean.
- **Schema flexibility** — Column names are resolved automatically from aliases. If your AIS data uses non-standard field names, add aliases to the `CONFIG` block in `ddt_ais_pipeline.py`.
- **AI summaries** — Require the `ANTHROPIC_API_KEY` environment variable and the `anthropic` Python package. The pipeline uses `claude-sonnet-4-5` for generation.
- **NMEA support** — Requires `pyais`: `pip install pyais`
- **Date filter guidance** — When working with the full 8M+ row dataset, use the date-range option to filter to a specific day during testing. Full-dataset runs require sufficient RAM and processing time.

---

<div align="center">

**DDT Team &nbsp;·&nbsp; BMIS 476 &nbsp;·&nbsp; GEN AI Data Processing & Analytics Solution**

</div>
