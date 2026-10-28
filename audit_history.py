
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent
HISTORY_DIR = BASE_DIR / "data" / "audit_history"
HISTORY_FILE = HISTORY_DIR / "runs.json"
RULESET_VERSION = "1.1"


def dataset_fingerprint(df):
    """Create a repeatable hash of the dataset being audited."""
    normalized = df.copy()
    normalized = normalized.reindex(sorted(normalized.columns), axis=1)
    normalized = normalized.fillna("").astype(str)
    normalized = normalized.sort_values(
        by=list(normalized.columns),
        kind="stable",
    ).reset_index(drop=True)

    content = normalized.to_csv(index=False, lineterminator="\n")
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_history():
    if not HISTORY_FILE.exists():
        return []

    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("History must be a JSON list.")

        return data

    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(
            f"Unable to read audit history: {exc}"
        ) from exc


def record_audit(df, findings, source_name):
    """Save a new audit run and its findings snapshot."""

    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    run_id = str(uuid.uuid4())
    run_time = datetime.now(timezone.utc).isoformat(timespec="seconds")
    fingerprint = dataset_fingerprint(df)

    severity_counts = (
        findings["severity"].value_counts().to_dict()
        if not findings.empty else {}
    )

    run_record = {
        "run_id": run_id,
        "run_time_utc": run_time,
        "source_name": source_name,
        "dataset_sha256": fingerprint,
        "ruleset_version": RULESET_VERSION,
        "accounts_reviewed": int(len(df)),
        "findings_count": int(len(findings)),
        "unique_affected_accounts": (
            int(findings["employee_id"].nunique())
            if not findings.empty else 0
        ),
        "severity_counts": severity_counts,
        "findings": findings.fillna("").to_dict(orient="records"),
    }

    history = load_history()
    history.append(run_record)

    temporary_file = HISTORY_FILE.with_suffix(".tmp")

    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(history, file, indent=2, ensure_ascii=False)

        temporary_file.replace(HISTORY_FILE)

    except OSError as exc:
        raise RuntimeError(
            f"Unable to save audit history: {exc}"
        ) from exc

    return run_record