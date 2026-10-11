---
name: codex-usage-report
description: Export privacy-minimised aggregate Codex token usage from local session history into a reviewable JSON file. Use when a user wants to contribute a Codex usage benchmark without sharing prompts or transcripts.
---

# Codex usage report

This skill produces a **local-only** report. Never upload, transmit, commit, or paste its contents without a separate explicit request.

1. Explain that the report contains aggregate token counts, model identifiers and coarse time buckets. These can still reveal patterns of activity.
2. Ask the user whether to proceed before reading session history. The default path is `~/.codex/sessions`; allow `CODEX_HOME` or `--sessions-dir` to override it.
3. From the root of this repository, run `python3 scripts/export_usage.py --output codex-usage-report.json` (or pass an absolute output path). Do not use network access.
4. Show the output file path, the number of files inspected, the number of usable usage snapshots, and any warnings. Encourage the user to inspect the JSON before sharing.
5. If the report is empty, explain that the supported local session format may differ. Do not fabricate usage.
6. Do not infer subscription capacity or a five-hour quota from token counts. Do not add usernames, prompts, transcripts, project names, filesystem paths or raw session IDs to the report.

The script reads JSONL records, extracts cumulative `token_count` snapshots from `event_msg` records, and retains only the latest cumulative snapshot per session. Session-level output is **not** exported. See `docs/privacy.md`.
