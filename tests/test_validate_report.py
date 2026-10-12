import copy
import unittest

from scripts.validate_report import InvalidReport, validate


def report():
    return {
        "schemaVersion": 1, "collectorVersion": "0.1.0",
        "dataType": "aggregate_token_usage", "privacy": "monthly-model-aggregates",
        "summary": {"filesInspected": 1, "usableSessions": 1, "snapshotsFound": 2, "skippedFiles": 0},
        "buckets": [{"month": "2026-10", "model": "gpt-6.1-sol", "sessions": 1,
                     "input_tokens": 100, "cached_input_tokens": 20, "output_tokens": 30,
                     "reasoning_output_tokens": 10, "total_tokens": 130}],
    }


class ValidationTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate(report())["summary"]["usableSessions"], 1)

    def test_reject_private_fields(self):
        item = report()
        item["buckets"][0]["projectPath"] = "/private/repo"
        with self.assertRaises(InvalidReport):
            validate(item)

    def test_reject_duplicate_buckets(self):
        item = report()
        item["buckets"].append(copy.deepcopy(item["buckets"][0]))
        item["summary"]["usableSessions"] = 2
        item["summary"]["filesInspected"] = 2
        with self.assertRaises(InvalidReport):
            validate(item)

    def test_reject_bad_values(self):
        for field, value in [("sessions", True), ("month", "2026-13"), ("model", "path/secret"),
                             ("cached_input_tokens", 101), ("total_tokens", 10)]:
            with self.subTest(field=field):
                item = report()
                item["buckets"][0][field] = value
                with self.assertRaises(InvalidReport):
                    validate(item)

    def test_reject_mismatched_counts(self):
        item = report()
        item["summary"]["usableSessions"] = 99
        with self.assertRaises(InvalidReport):
            validate(item)

class SharedContractTests(unittest.TestCase):
    def test_shared_website_validation_cases(self):
        import json
        from pathlib import Path
        cases = json.loads((Path(__file__).parent / "fixtures" / "report-validation.json").read_text())
        for case in cases:
            with self.subTest(case=case["name"]):
                if case["valid"]:
                    validate(case["report"])
                else:
                    with self.assertRaises(InvalidReport):
                        validate(case["report"])


if __name__ == "__main__":
    unittest.main()
