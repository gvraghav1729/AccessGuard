import unittest
from datetime import date, timedelta

import pandas as pd

from audit_engine import run_audit, validate_data


def make_employee(
    employee_id="E001",
    employment_status="Active",
    account_status="Active",
    role="Analyst",
    last_login=None,
    permissions="view_reports",
):
    """Build one synthetic employee record for testing."""

    if last_login is None:
        last_login = date.today().isoformat()

    return {
        "employee_id": employee_id,
        "employee_name": "Test Employee",
        "department": "Finance",
        "employment_status": employment_status,
        "account_status": account_status,
        "role": role,
        "last_login": last_login,
        "permissions": permissions,
    }


class AccessGuardTests(unittest.TestCase):

    def test_terminated_employee_with_active_account(self):
        employee = make_employee(
            employment_status="Terminated",
            account_status="Active",
        )

        findings = run_audit(pd.DataFrame([employee]))

        self.assertIn("AC-01", findings["rule_id"].tolist())

    def test_terminated_employee_with_disabled_account(self):
        employee = make_employee(
            employment_status="Terminated",
            account_status="Disabled",
        )

        findings = run_audit(pd.DataFrame([employee]))

        self.assertNotIn("AC-01", findings["rule_id"].tolist())

    def test_admin_role_is_flagged_for_review(self):
        employee = make_employee(role="Admin")

        findings = run_audit(pd.DataFrame([employee]))

        self.assertIn("AC-02", findings["rule_id"].tolist())

    def test_regular_role_is_not_flagged_as_privileged(self):
        employee = make_employee(role="Analyst")

        findings = run_audit(pd.DataFrame([employee]))

        self.assertNotIn("AC-02", findings["rule_id"].tolist())

    def test_conflicting_permissions_are_flagged(self):
        employee = make_employee(
            permissions="create_vendor;approve_payment"
        )

        findings = run_audit(pd.DataFrame([employee]))

        self.assertIn("AC-03", findings["rule_id"].tolist())

    def test_unrelated_permissions_are_not_flagged(self):
        employee = make_employee(
            permissions="view_reports;export_reports"
        )

        findings = run_audit(pd.DataFrame([employee]))

        self.assertNotIn("AC-03", findings["rule_id"].tolist())

    def test_account_inactive_for_more_than_90_days(self):
        old_date = (
            date.today() - timedelta(days=91)
        ).isoformat()

        employee = make_employee(last_login=old_date)

        findings = run_audit(pd.DataFrame([employee]))

        self.assertIn("AC-04", findings["rule_id"].tolist())

    def test_account_used_exactly_90_days_ago(self):
        old_date = (
            date.today() - timedelta(days=90)
        ).isoformat()

        employee = make_employee(last_login=old_date)

        findings = run_audit(pd.DataFrame([employee]))

        self.assertNotIn("AC-04", findings["rule_id"].tolist())

    def test_recently_used_account_is_not_dormant(self):
        recent_date = (
            date.today() - timedelta(days=10)
        ).isoformat()

        employee = make_employee(last_login=recent_date)

        findings = run_audit(pd.DataFrame([employee]))

        self.assertNotIn("AC-04", findings["rule_id"].tolist())

    def test_disabled_account_is_not_flagged_as_dormant(self):
        old_date = (
            date.today() - timedelta(days=120)
        ).isoformat()

        employee = make_employee(
            account_status="Disabled",
            last_login=old_date,
        )

        findings = run_audit(pd.DataFrame([employee]))

        self.assertNotIn("AC-04", findings["rule_id"].tolist())

    def test_all_four_rules_can_detect_findings(self):
        employees = pd.DataFrame([
            make_employee(
                employee_id="E001",
                employment_status="Terminated",
                account_status="Active",
            ),
            make_employee(
                employee_id="E002",
                role="Admin",
            ),
            make_employee(
                employee_id="E003",
                permissions="create_vendor;approve_payment",
            ),
            make_employee(
                employee_id="E004",
                last_login=(
                    date.today() - timedelta(days=120)
                ).isoformat(),
            ),
        ])

        findings = run_audit(employees)

        self.assertEqual(
            set(findings["rule_id"]),
            {"AC-01", "AC-02", "AC-03", "AC-04"},
        )

    def test_missing_required_column_is_rejected(self):
        employee = make_employee()
        del employee["department"]

        with self.assertRaisesRegex(
            ValueError, "department"
        ):
            validate_data(pd.DataFrame([employee]))

    def test_duplicate_employee_ids_are_rejected(self):
        employees = pd.DataFrame([
            make_employee(employee_id="E001"),
            make_employee(employee_id="E001"),
        ])

        with self.assertRaisesRegex(
            ValueError, "unique"
        ):
            run_audit(employees)

    def test_empty_dataset_is_rejected(self):
        employees = pd.DataFrame(columns=[
            "employee_id",
            "employee_name",
            "department",
            "employment_status",
            "account_status",
            "role",
            "last_login",
            "permissions",
        ])

        with self.assertRaisesRegex(
            ValueError, "empty"
        ):
            run_audit(employees)
    
    def test_missing_last_login_is_flagged(self):
        employee = make_employee(last_login="")

        findings = run_audit(pd.DataFrame([employee]))

        self.assertIn("AC-05", findings["rule_id"].tolist())
        self.assertNotIn("AC-04", findings["rule_id"].tolist())

    def test_invalid_last_login_is_flagged(self):
        employee = make_employee(last_login="not-a-date")

        findings = run_audit(pd.DataFrame([employee]))

        self.assertIn("AC-05", findings["rule_id"].tolist())
        self.assertNotIn("AC-04", findings["rule_id"].tolist())

    def test_future_last_login_is_flagged(self):
        future_date = (
            date.today() + timedelta(days=5)
        ).isoformat()

        employee = make_employee(last_login=future_date)

        findings = run_audit(pd.DataFrame([employee]))

        self.assertIn("AC-05", findings["rule_id"].tolist())
        self.assertNotIn("AC-04", findings["rule_id"].tolist())

    def test_blank_employee_id_is_rejected(self):
        employee = make_employee(employee_id="   ")

        with self.assertRaisesRegex(ValueError, "employee_id"):
            run_audit(pd.DataFrame([employee]))

    def test_case_insensitive_duplicate_ids_are_rejected(self):
        employees = pd.DataFrame([
            make_employee(employee_id="E001"),
            make_employee(employee_id="e001"),
        ])

        with self.assertRaisesRegex(ValueError, "unique"):
            run_audit(employees)


if __name__ == "__main__":
    unittest.main(verbosity=2)