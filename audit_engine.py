
import pandas as pd

REQUIRED_COLUMNS = [
    "employee_id",
    "employee_name",
    "department",
    "employment_status",
    "account_status",
    "role",
    "last_login",
    "permissions",
]

FINDING_COLUMNS = [
    "finding_id",
    "employee_id",
    "employee_name",
    "rule_id",
    "finding",
    "severity",
    "evidence",
    "recommended_action",
]


def validate_data(df):
    """Validate the structure and identity fields of the dataset."""

    missing = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing)
        )

    if df.empty:
        raise ValueError("The uploaded dataset is empty.")

    result = df.copy()

    for column in ["employee_id", "employee_name"]:
        result[column] = result[column].astype("string").str.strip()

        if result[column].isna().any():
            raise ValueError(f"{column} cannot be blank.")

        if result[column].eq("").any():
            raise ValueError(f"{column} cannot be blank.")

    normalized_ids = result["employee_id"].str.casefold()

    if normalized_ids.duplicated().any():
        raise ValueError("Employee IDs must be unique.")

    return result


def run_audit(df):
    """Run deterministic access-control and data-quality checks."""

    df = validate_data(df)
    findings = []

    today = pd.Timestamp.now().normalize()

    for _, employee in df.iterrows():
        employee_id = str(employee["employee_id"]).strip()
        name = str(employee["employee_name"]).strip()

        status = str(employee["employment_status"]).strip().casefold()
        account = str(employee["account_status"]).strip().casefold()
        role = str(employee["role"]).strip().casefold()

        permissions_raw = employee["permissions"]

        if pd.isna(permissions_raw):
            permissions_text = ""
        else:
            permissions_text = str(permissions_raw)

        permissions = {
            item.strip().casefold()
            for item in permissions_text.split(";")
            if item.strip()
        }

        def add_finding(
            rule_id, title, severity, evidence, action
        ):
            findings.append({
                "finding_id": f"{employee_id}-{rule_id}",
                "employee_id": employee_id,
                "employee_name": name,
                "rule_id": rule_id,
                "finding": title,
                "severity": severity,
                "evidence": evidence,
                "recommended_action": action,
            })

        # AC-01: Terminated employees with active accounts
        if status == "terminated" and account == "active":
            add_finding(
                "AC-01",
                "Terminated employee with active account",
                "Critical",
                "Employment is terminated but the account is active.",
                "Confirm termination and verify access revocation."
            )

        # AC-02: Privileged accounts requiring review
        if role in {"admin", "administrator", "superadmin"}:
            add_finding(
                "AC-02",
                "Privileged account requires review",
                "High",
                f"Assigned role: {role}.",
                "Verify business justification, approval and "
                "appropriate privilege restrictions."
            )

        # AC-03: Specified segregation-of-duties conflict
        if (
            "create_vendor" in permissions
            and "approve_payment" in permissions
        ):
            add_finding(
                "AC-03",
                "Potential segregation-of-duties conflict",
                "High",
                "The account can create vendors and approve payments.",
                "Review the effective permissions and separate "
                "conflicting duties where appropriate."
            )

        # AC-04: Active accounts inactive for more than 90 days
        raw_login = employee["last_login"]

        if pd.isna(raw_login) or not str(raw_login).strip():
            last_login = pd.NaT
        else:
            last_login = pd.to_datetime(
                raw_login, errors="coerce"
            )

        if pd.notna(last_login):
            last_login = pd.Timestamp(last_login)

            # Normalize timezone-aware values to comparable dates.
            if last_login.tzinfo is not None:
                last_login = (
                    last_login.tz_convert(None)
                    if last_login.tzinfo
                    else last_login
                )

        invalid_login = (
            pd.isna(last_login)
            or (
                pd.notna(last_login)
                and last_login.normalize() > today
            )
        )

        if invalid_login:
            add_finding(
                "AC-05",
                "Missing or invalid last-login date",
                "Medium",
                f"Recorded last_login value: {raw_login!r}.",
                "Verify the source data and obtain a valid login date "
                "before concluding the dormant-account test."
            )

        elif (
            account == "active"
            and (today - last_login.normalize()).days > 90
        ):
            add_finding(
                "AC-04",
                "Active account with no recent login",
                "Medium",
                f"Last login: {last_login.date()}.",
                "Confirm continued business need and investigate "
                "whether the account should be disabled."
            )

    return pd.DataFrame(findings, columns=FINDING_COLUMNS)