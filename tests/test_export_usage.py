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


if __name__ == "__main__":
    unittest.main()
