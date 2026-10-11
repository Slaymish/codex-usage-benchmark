# Codex usage benchmark

A community-powered, privacy-first Codex usage benchmark, intended to inform a subscription cost calculator on an Astro website.

## Local export (first prototype)

No separate app or service is needed. A [Codex skill](skills/codex-usage-report/SKILL.md) instructs Codex to run the standard-library Python exporter on your local Codex history. The skill can be installed or copied into a Codex skills directory according to your Codex installation's supported skill workflow.

You can also run the exporter directly:

```sh
python3 scripts/export_usage.py --output codex-usage-report.json
```

This scans `~/.codex/sessions` (or `$CODEX_HOME/sessions`). To specify a different directory:

```sh
python3 scripts/export_usage.py --sessions-dir /path/to/sessions --output codex-usage-report.json
```

**Review the JSON before sharing it.** The report contains aggregate monthly token counts by model and session counts; it does not include prompts, transcripts or filenames. It is not guaranteed anonymous. No automatic upload or contribution endpoint exists yet.

The exporter intentionally does not estimate Codex quotas or costs from tokens. Its data is a starting point for benchmarking, not sufficient evidence to optimise subscriptions. See [privacy and measurement notes](docs/privacy.md).

## Development

Requires Python 3.10+; no third-party dependencies.

```sh
python3 -m unittest discover -s tests -v
```

## Status

Prototype exporter and skill. Planned next: verify Codex telemetry compatibility against consenting test data, strengthen model attribution and privacy, then implement explicit user-reviewed uploads and aggregate statistics.
