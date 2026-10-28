# AccessGuard — IT Access Control Auditor

**AccessGuard** is a Python-based, rule-driven screening application
that reviews employee access records, flags potential access-control
exceptions, supports remediation tracking, compares audit runs, and
generates downloadable reports.

> **Version:** 1.0  
> **Purpose:** Portfolio project demonstrating concepts relevant to IT
> audit, technology risk, access governance, and control testing.  
> **Disclaimer:** AccessGuard is a screening demonstration tool. It is
> not a certified security product, does not connect to a live identity
> provider, and does not produce a formal audit opinion.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Control Rules](#control-rules)
- [How It Works](#how-it-works)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Running the Tests](#running-the-tests)
- [Using AccessGuard](#using-accessguard)
- [Exporting Reports](#exporting-reports)
- [Data and Privacy](#data-and-privacy)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)

## Overview

Access governance is an important part of technology risk management.
Accounts that remain active after an employee leaves, excessive
privileges, or conflicting permissions can expose an organisation to
operational, financial, and compliance risks.

AccessGuard demonstrates how a repeatable set of screening rules can be
applied to employee access records. It presents potential exceptions in
a dashboard and allows reviewers to inspect findings, record remediation
actions, retain audit-run snapshots, and compare results across runs.

Findings must be validated against business context and supporting
evidence before an audit conclusion is reached.

## Key Features

- **Access-control screening:** Evaluates supplied employee records
  against five predefined rules.
- **Risk dashboard:** Summarises reviewed accounts and findings by
  severity and control.
- **Findings workbench:** Supports searching and filtering findings,
  inspecting evidence, and reviewing recommended actions.
- **Remediation tracking:** Tracks remediation status and related
  follow-up details.
- **Audit history:** Saves audit-run snapshots with run identifiers and
  timestamps.
- **Run comparison:** Classifies findings between saved runs as new,
  continuing, or resolved according to the comparison logic.
- **CSV exports:** Exports tabular results for use in other tools.
- **Formatted Excel exports:** Generates styled `.xlsx` workbooks with
  readable headers, filters, wrapped text, and adjusted column widths.
- **PDF reports:** Generates screening reports with summary metrics,
  detailed findings, methodology, and limitations.
- **Automated tests:** Includes unit tests for the audit rules and
  run-comparison logic.

## Control Rules

| Rule ID | Check                                                                  | Severity | Why it matters                                                                  |
|---------|------------------------------------------------------------------------|----------|---------------------------------------------------------------------------------|
| AC-01   | An employee is marked terminated while their account remains active.   | Critical | May indicate that access was not revoked after termination.                     |
| AC-02   | An account has a privileged role, such as administrator.               | High     | Privileged access should have an appropriate business justification and review. |
| AC-03   | An account has both `create_vendor` and `approve_payment` permissions. | High     | May represent a segregation-of-duties conflict that needs review.               |
| AC-04   | An active account has not logged in for more than 90 days.             | Medium   | May indicate an account that needs a business-need review.                      |
| AC-05   | The last-login date is missing, invalid, or in the future.             | Medium   | Incomplete or inconsistent data can prevent reliable access review.             |

Severity represents the configured screening priority. It is not a
confirmed finding of misconduct or a definitive risk rating. These rules
are deliberately simple and should be adapted and validated before use
in a real environment.

## How It Works

1.  **Input:** Employee access records are supplied through the sample
    dataset or a CSV upload, depending on the workflow.
2.  **Validation:** Required fields and basic data-quality issues are
    checked.
3.  **Screening:** The audit engine evaluates records against the
    configured rules.
4.  **Review:** Findings are presented with a control identifier,
    severity, evidence, and recommended action.
5.  **Remediation:** A reviewer can record follow-up status and related
    details.
6.  **History and comparison:** Audit runs can be saved and compared to
    identify new, continuing, and resolved findings.
7.  **Reporting:** Results can be exported as CSV, formatted Excel
    workbooks, and PDF screening reports.

A finding disappearing from a later run does **not** prove that the
underlying issue was remediated. Reviewers should confirm remediation
using appropriate evidence.

## Technology Stack

- **Python** — application logic and rule evaluation
- **Streamlit** — interactive web interface
- **Pandas** — tabular data processing
- **Plotly** — dashboard charts
- **ReportLab** — PDF report generation
- **OpenPyXL** — formatted Excel workbook generation
- **unittest** — automated testing
- **CSV and JSON** — sample data and local persistence

## Project Structure

``` text
AccessGuard/
├── app.py
├── audit_engine.py
├── audit_history.py
├── audit_comparison.py
├── report_generator.py
├── data/
│   ├── employees.csv
│   ├── remediation.json
│   └── audit_history/
├── tests/
│   ├── test_audit_engine.py
│   └── test_audit_comparison.py
├── .streamlit/
│   └── config.toml
├── requirements.txt
├── .gitignore
└── README.md
```

This is a representative structure. Keep the README aligned with the
actual files in your repository. Local audit-history files and
remediation data may be created or updated when the application runs.

## Getting Started

### Prerequisites

- Python 3.10 or later recommended
- `pip`
- Git (optional, for version control)

### 1. Clone the repository

Replace the placeholders with your GitHub username and repository name:

``` bash
git clone https://github.com/gvraghav1729/AccessGuard.git
cd <AccessGuard>
```

Alternatively, download the repository ZIP and extract it.

### 2. Create a virtual environment

**Windows — Command Prompt**

``` bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows — PowerShell**

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Ensure `requirements.txt` includes the packages used by the application,
including `streamlit`, `pandas`, `plotly`, `reportlab`, and `openpyxl`.

### 4. Run AccessGuard

``` bash
python -m streamlit run app.py
```

Streamlit will display a local URL in the terminal, usually
`http://localhost:8501`. Open that URL in your browser.

## Running the Tests

Run the automated test suite from the project root with the virtual
environment activated:

``` bash
python -m unittest discover -s tests -v
```

A successful run should finish with `OK`. If a test fails, inspect the
failure details before treating the release as verified.

The test suite covers the implemented audit-engine and run-comparison
behaviour. Manual end-to-end checks are also recommended for the
interface, persistence, and PDF/Excel exports.

## Using AccessGuard

1.  Start the application.
2.  Review the dashboard summary.
3.  Open the findings workbench and filter by severity or control.
4.  Inspect the evidence and recommended action for a finding.
5.  Update remediation details when appropriate.
6.  Run another audit and save it to history.
7.  Compare saved runs and review new, continuing, and resolved
    classifications.
8.  Export the results in the required format.

Exact controls and labels may change as the interface evolves.

## Exporting Reports

- **CSV:** Best for interoperability with scripts, databases, and other
  analysis tools. CSV files do not retain styling, colours, fonts, or
  column widths.
- **Excel (`.xlsx`):** Best for reviewing and presenting tabular data
  with styled headers, filters, wrapped text, and readable column
  widths.
- **PDF:** Best for sharing a screening report containing summary
  information, detailed findings, methodology, and limitations.

Review exports before sharing them. They may contain employee
identifiers or other sensitive information if real data is used.

## Data and Privacy

The included dataset is intended for demonstration. Use synthetic or
appropriately anonymised records when demonstrating the project
publicly.

Audit history and remediation information may be stored locally in JSON
files under `data/`. Check the repository contents and `.gitignore`
before committing. Do not publish confidential employee data,
credentials, secrets, or production audit records.

If you adapt AccessGuard for real organisational data, establish
appropriate access controls, retention rules, secure storage, and
approval before processing or exporting that data.

## Limitations

- The application uses predefined, rule-based checks; it does not
  perform a comprehensive security audit.
- Results depend on the completeness, accuracy, and format of the input
  data.
- A privileged role is flagged for review; its presence does not
  automatically mean the access is inappropriate.
- A potential segregation-of-duties conflict requires validation against
  organisational policies and business processes.
- A finding classified as resolved between runs may simply be absent
  from the newer dataset; this is not proof of remediation.
- The application does not independently inspect identity-provider
  configurations, access logs, approval records, or production systems.
- This portfolio demonstration does not replace qualified audit
  judgement or a formal audit opinion.

## Future Improvements

Possible future extensions include:

- Integration with identity and access management platforms
- Configurable rules and organisation-specific control mappings
- Role-based access to the application and its records
- Database-backed audit history and remediation tracking
- Evidence attachments and remediation verification
- More extensive input validation and test coverage
- Deployment with appropriate authentication, logging, and security
  controls

These are potential enhancements, not claims about current
functionality.

------------------------------------------------------------------------

## Author

**Raghav Gudlavalleti**  
GitHub: [gvraghav1729](https://github.com/gvraghav1729)

*AccessGuard V1.0 — an IT access-control screening and technology-risk
portfolio project.*
