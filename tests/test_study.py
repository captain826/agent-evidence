import unittest

from agent_evidence.core import InvalidTrace
from agent_evidence.study import describe_study


def entry(name, arm="baseline", claimed=True, verified=True, authorized=True):
    return {
        "run_id": name,
        "arm": arm,
        "completion_claimed": claimed,
        "verified_completion": verified,
        "approved_actions": authorized,
    }


class StudyDescriptiveTests(unittest.TestCase):
    def test_one_supported_claim(self):
        x = describe_study({"runs": [entry("a")]})["summary"]
        self.assertEqual(x["unsupported_adjudicated_claims"], 0)
        self.assertEqual(x["unsupported_claim_rate_among_adjudicated"], 0.0)

    def test_failed_independent_check(self):
        x = describe_study({"runs": [entry("a", verified=False)]})["summary"]
        self.assertEqual(x["unsupported_claim_rate_among_adjudicated"], 1.0)

    def test_authorization_violation(self):
        x = describe_study({"runs": [entry("a", authorized=False)]})["summary"]
        self.assertEqual(x["unsupported_adjudicated_claims"], 1)

    def test_missing_adjudication_excluded_from_denominator(self):
        d = describe_study({"runs": [entry("a", verified=None), entry("b", verified=False)]})["summary"]
        self.assertEqual(d["adjudicated_claims"], 1)
        self.assertEqual(d["unresolved_claims"], 1)
        self.assertEqual(d["unsupported_claim_rate_among_adjudicated"], 1.0)

    def test_no_completion_claim_is_not_denominator(self):
        d = describe_study({"runs": [entry("a", claimed=False, verified=False)]})["summary"]
        self.assertEqual(d["completion_claims"], 0)
        self.assertIsNone(d["unsupported_claim_rate_among_adjudicated"])

    def test_group_counts_reconcile(self):
        runs = [entry("a"), entry("b", arm="evidence_gate", verified=False)]
        d = describe_study({"runs": runs})
        self.assertEqual(sum(v["runs"] for v in d["arms"].values()), 2)
        self.assertFalse(d["causal_claims_supported"])

    def test_invalid_arm(self):
        with self.assertRaises(InvalidTrace):
            describe_study({"runs": [entry("a", arm="other")]})

    def test_arm_with_unhashable_type_rejected(self):
        with self.assertRaises(InvalidTrace):
            describe_study({"runs": [entry("a", arm=[])]})

    def test_duplicate_ids(self):
        with self.assertRaises(InvalidTrace):
            describe_study({"runs": [entry("a"), entry("a")]})

    def test_invalid_boolean(self):
        with self.assertRaises(InvalidTrace):
            describe_study({"runs": [entry("a", verified="True")]})

    def test_empty_study(self):
        x = describe_study({"runs": []})["summary"]
        self.assertEqual(x["runs"], 0)
        self.assertIsNone(x["unsupported_claim_rate_among_adjudicated"])

    def test_all_unresolved_rate_null(self):
        x = describe_study({"runs": [entry("a", verified=None)]})["summary"]
        self.assertEqual(x["unresolved_claims"], 1)
        self.assertIsNone(x["unsupported_claim_rate_among_adjudicated"])


if __name__ == "__main__":
    unittest.main()
