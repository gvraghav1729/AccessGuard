
import pandas as pd

def compare_audit_runs(older_run, newer_run):
    """
    Compare two saved audit runs using employee ID and rule ID.
    """

    older_findings = pd.DataFrame(older_run.get("findings", []))
    newer_findings = pd.DataFrame(newer_run.get("findings", []))

    key_columns = ["employee_id", "rule_id"]

    for frame in (older_findings, newer_findings):
        for column in key_columns:
            if column not in frame.columns:
                frame[column] = pd.Series(dtype="string")

    older_keys = set(
        zip(
            older_findings["employee_id"].astype(str),
            older_findings["rule_id"].astype(str),
        )
    )

    newer_keys = set(
        zip(
            newer_findings["employee_id"].astype(str),
            newer_findings["rule_id"].astype(str),
        )
    )

    resolved_keys = older_keys - newer_keys
    continuing_keys = older_keys & newer_keys
    new_keys = newer_keys - older_keys

    def rows_for_keys(frame, keys, status):
        if not keys:
            return pd.DataFrame()

        mask = [
            (str(employee_id), str(rule_id)) in keys
            for employee_id, rule_id in zip(
                frame["employee_id"], frame["rule_id"]
            )
        ]

        result = frame.loc[mask].copy()
        result.insert(0, "comparison_status", status)
        return result

    resolved = rows_for_keys(older_findings, resolved_keys, "Resolved")
    continuing = rows_for_keys(
        newer_findings, continuing_keys, "Continuing"
    )
    new = rows_for_keys(newer_findings, new_keys, "New")

    return pd.concat(
        [resolved, continuing, new],
        ignore_index=True,
    )
