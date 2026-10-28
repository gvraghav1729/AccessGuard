
import unittest

from audit_comparison import compare_audit_runs


def make_run(findings):
    return {"findings": findings}


def make_finding(employee_id, rule_id, severity="High"):
    return {
        "employee_id": employee_id,
        "rule_id": rule_id,
        "finding_id": f"{employee_id}-{rule_id}",
        "finding": f"Test finding for {rule_id}",
        "severity": severity,
    }


class TestAuditComparison(unittest.TestCase):

    def test_identical_runs_are_continuing(self):
        finding = make_finding("E001", "AC-02")

        result = compare_audit_runs(
            make_run([finding]),
            make_run([finding]),
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result.iloc[0]["comparison_status"],
            "Continuing",
        )

    def test_removed_finding_is_resolved(self):
        older = make_run([
            make_finding("E001", "AC-01")
        ])
        newer = make_run([])

        result = compare_audit_runs(older, newer)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result.iloc[0]["comparison_status"],
            "Resolved",
        )

    def test_added_finding_is_new(self):
        older = make_run([])
        newer = make_run([
            make_finding("E002", "AC-03")
        ])

        result = compare_audit_runs(older, newer)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result.iloc[0]["comparison_status"],
            "New",
        )

    def test_mixed_changes(self):
        older = make_run([
            make_finding("E001", "AC-01"),
            make_finding("E002", "AC-02"),
        ])
        newer = make_run([
            make_finding("E002", "AC-02"),
            make_finding("E003", "AC-03"),
        ])

        result = compare_audit_runs(older, newer)

        counts = result["comparison_status"].value_counts().to_dict()

        self.assertEqual(counts.get("Resolved", 0), 1)
        self.assertEqual(counts.get("Continuing", 0), 1)
        self.assertEqual(counts.get("New", 0), 1)

    def test_both_runs_without_findings(self):
        result = compare_audit_runs(
            make_run([]),
            make_run([]),
        )

        self.assertTrue(result.empty)


if __name__ == "__main__":
    unittest.main()