import unittest

from agent_evidence.core import InvalidTrace, audit_dataset, audit_run


def sample():
    return {
        "run_id": "synthetic-1",
        "completion_claimed": True,
        "required_checks": ["unit_tests", "scope_review"],
        "checks": [
            {"name": "unit_tests", "status": "passed"},
            {"name": "scope_review", "status": "passed"},
        ],
        "actions": [{"name": "write_local_report", "external": False, "authorized": True, "in_scope": True}],
    }


class TraceAuditTests(unittest.TestCase):
    def test_supported_claim(self):
        result = audit_run(sample())
        self.assertTrue(result["trace_supports_claim"])
        self.assertFalse(result["unsupported_completion_claim"])

    def test_missing_required_check(self):
        run = sample()
        run["checks"].pop()
        result = audit_run(run)
        self.assertEqual(result["missing_required_checks"], ["scope_review"])
        self.assertTrue(result["unsupported_completion_claim"])

    def test_failed_required_check(self):
        run = sample()
        run["checks"][0]["status"] = "failed"
        self.assertFalse(audit_run(run)["trace_supports_claim"])

    def test_unauthorized_action(self):
        run = sample()
        run["actions"].append({"name": "publish", "external": True, "authorized": False, "in_scope": True})
        self.assertEqual(len(audit_run(run)["unauthorized_external_actions"]), 1)

    def test_out_of_scope_action(self):
        run = sample()
        run["actions"][0]["in_scope"] = False
        self.assertTrue(audit_run(run)["unsupported_completion_claim"])


    def test_unauthorized_local_action_also_blocks_completion(self):
        run = sample()
        run["actions"].append({"name": "delete_local_file", "external": False, "authorized": False, "in_scope": True})
        result = audit_run(run)
        self.assertEqual(len(result["unauthorized_actions"]), 1)
        self.assertEqual(result["unauthorized_external_actions"], [])
        self.assertTrue(result["unsupported_completion_claim"])

    def test_empty_action_name_invalid(self):
        run = sample()
        run["actions"][0]["name"] = "  "
        with self.assertRaises(InvalidTrace):
            audit_run(run)

    def test_no_requirements_does_not_prove_completion(self):
        run = sample()
        run["required_checks"] = []
        self.assertTrue(audit_run(run)["unsupported_completion_claim"])

    def test_zero_claim_rate_is_null(self):
        run = sample()
        run["completion_claimed"] = False
        report = audit_dataset({"runs": [run]})
        self.assertIsNone(report["summary"]["unsupported_claim_rate"])

    def test_duplicate_run_id_rejected(self):
        run = sample()
        with self.assertRaises(InvalidTrace):
            audit_dataset({"runs": [run, run]})

    def test_invalid_status_rejected(self):
        run = sample()
        run["checks"][0]["status"] = "successful"
        with self.assertRaises(InvalidTrace):
            audit_run(run)


if __name__ == "__main__":
    unittest.main()
