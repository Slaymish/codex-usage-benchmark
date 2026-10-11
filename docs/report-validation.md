# Report validation

Validate a local export before sharing:

```sh
python3 scripts/validate_report.py codex-usage-report.json
python3 -m unittest discover -s tests -v
```

Validation is strict: only the documented v1 aggregate fields are accepted. Extra fields (including accidental private content), negative/boolean token values, duplicate month/model buckets, inconsistent counts, invalid months, unsupported versions and files larger than 256 KB are rejected.

This is **not** an upload endpoint or proof of anonymity. A malicious submitter can fabricate plausible totals. Public aggregation will need contributor-level deduplication, abuse prevention, privacy thresholds, retention and withdrawal controls. A report cannot measure five-hour quotas or active coding time.
