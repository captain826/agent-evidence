import copy
import unittest

from agent_evidence.consumer_reasoning import (
    FRAMES, independent_affordability_cap, make_pilot_cases, validate_pilot_cases,
)


class ConsumerReasoningTests(unittest.TestCase):
    def test_exact_number_of_variants(self):
        self.assertEqual(len(make_pilot_cases()), 36)

    def test_all_pairs_match_except_frame(self):
        self.assertEqual(validate_pilot_cases(make_pilot_cases())["paired_scenarios"], 12)

    def test_frames_are_all_present(self):
        x = validate_pilot_cases(make_pilot_cases())
        self.assertEqual(x["frames"], sorted(FRAMES))

    def test_cap_math(self):
        self.assertEqual(independent_affordability_cap(
            {"available_funds": 500, "mandatory_outlays": 250,
             "minimum_reserve": 125}), "125.00")

    def test_shortfall_cap_is_zero(self):
        self.assertEqual(independent_affordability_cap(
            {"available_funds": 60, "mandatory_outlays": 80,
             "minimum_reserve": 10}), "0.00")

    def test_missing_information_is_not_zero(self):
        self.assertIsNone(independent_affordability_cap(
            {"available_funds": 50, "mandatory_outlays": None,
             "minimum_reserve": 10}))

    def test_nan_rejected(self):
        with self.assertRaises(ValueError):
            independent_affordability_cap(
                {"available_funds": float("nan"), "mandatory_outlays": 10,
                 "minimum_reserve": 10})

    def test_negative_rejected(self):
        with self.assertRaises(ValueError):
            independent_affordability_cap(
                {"available_funds": -1, "mandatory_outlays": 10,
                 "minimum_reserve": 10})

    def test_tampered_oracle_rejected(self):
        a = make_pilot_cases()
        a[0]["oracle_cap"] = "12345.00"
        with self.assertRaises(ValueError):
            validate_pilot_cases(a)

    def test_tampered_framing_facts_rejected(self):
        a = make_pilot_cases()
        a[1]["purchase_price"] += 1
        a[1]["price_within_cap"] = False
        with self.assertRaises(ValueError):
            validate_pilot_cases(a)

    def test_duplicate_id_rejected(self):
        a = make_pilot_cases()
        a[1]["id"] = a[0]["id"]
        with self.assertRaises(ValueError):
            validate_pilot_cases(a)

    def test_no_model_runs_implied(self):
        self.assertEqual(validate_pilot_cases(make_pilot_cases())["model_runs"], 0)

if __name__ == "__main__":
    unittest.main()
