import json
from pathlib import Path
import tempfile
import unittest

from scripts.export_usage import export, month_of, safe_model


class ExportTests(unittest.TestCase):
    def test_aggregate_and_ignore_private_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = root / "2026" / "10" / "sample.jsonl"
            session.parent.mkdir(parents=True)
            records = [
                {"type": "turn_context", "payload": {"model": "gpt-6.1-sol"}},
                {"type": "event_msg", "timestamp": "2026-10-11T12:00:00Z", "payload": {"type": "user_message", "message": "SECRET_PROMPT"}},
                {"type": "event_msg", "timestamp": "2026-10-11T12:00:00Z", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120}}}},
                {"type": "event_msg", "timestamp": "2026-10-11T12:01:00Z", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 200, "output_tokens": 40, "total_tokens": 240}}}},
            ]
            session.write_text("\n".join(json.dumps(r) for r in records))
            report = export(root)
            self.assertEqual(report["summary"]["usableSessions"], 1)
            self.assertEqual(report["buckets"][0]["input_tokens"], 200)
            self.assertEqual(report["buckets"][0]["output_tokens"], 40)
            self.assertNotIn("SECRET_PROMPT", json.dumps(report))
            self.assertNotIn(str(root), json.dumps(report))

    def test_no_sessions(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = export(Path(tmp))
            self.assertEqual(report["buckets"], [])

    def test_invalid_values(self):
        self.assertIsNone(month_of("not a date"))
        self.assertEqual(safe_model("private/path"), "unknown")

class TelemetryCompatibilityTests(unittest.TestCase):
    def test_missing_optional_totals_do_not_crash_multiple_snapshots(self):
        from scripts.validate_report import validate
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            records = [{"type": "turn_context", "payload": {"model": "gpt-6.1-sol"}}]
            for n in (100, 200):
                records.append({"type": "event_msg", "timestamp": "2026-10-12T00:00:00Z", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": n, "output_tokens": 20}}}})
            # A later context with no usage must not relabel the retained snapshot.
            records.append({"type": "turn_context", "payload": {"model": "gpt-other"}})
            (root / "synthetic.jsonl").write_text("\n".join(json.dumps(r) for r in records))
            report = validate(export(root))
            self.assertEqual(report["buckets"][0]["total_tokens"], 220)
            self.assertEqual(report["buckets"][0]["model"], "gpt-6.1-sol")
            self.assertEqual(report["summary"]["snapshotsFound"], 2)

    def test_unicode_and_newline_models_are_unknown(self):
        for model in ("private\n", "mödël"):
            self.assertEqual(safe_model(model), "unknown")

class InvalidOptionalTelemetryTests(unittest.TestCase):
    def test_invalid_present_optional_fields_are_not_fabricated_as_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = {"type": "event_msg", "timestamp": "2026-10-12T00:00:00Z", "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 100, "output_tokens": 20, "cached_input_tokens": -1}}}}
            (root / "synthetic.jsonl").write_text(json.dumps(bad))
            self.assertEqual(export(root)["summary"]["usableSessions"], 0)

class ExportContractTests(unittest.TestCase):
    def test_cli_refuses_invalid_aggregate_without_writing_output(self):
        import contextlib
        import io
        from unittest.mock import patch
        from scripts.export_usage import main
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            invalid = json.loads((Path(__file__).parent / "fixtures" / "report-validation.json").read_text())[0]["report"]
            invalid["summary"]["snapshotsFound"] = 0
            with patch("sys.argv", ["export_usage.py", "--sessions-dir", tmp, "--output", str(output)]), patch("scripts.export_usage.export", return_value=invalid), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(), 2)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
