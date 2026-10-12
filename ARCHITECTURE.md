# Architecture and contribution boundaries

scripts/export_usage.py reads only a user-authorised local session directory and
writes an aggregate schema-v1 JSON file. It uses the Python standard library,
never the network, and exports no prompts, tool calls, paths, repository names,
filenames, raw session IDs or precise timestamps. It retains the largest usable
cumulative snapshot per session, labelled with the model context and UTC month
of that snapshot. Sessions spanning months or switching models are still
approximate; this is not a model-accurate per-turn measurement.

Missing optional token telemetry defaults to zero for cache/reasoning counts
and input plus output for total tokens. Invalid present values and impossible
totals are skipped. ASCII model labels match the web contract; unsupported
labels become unknown. Collector version 0.1.1 marks these compatibility fixes.

scripts/validate_report.py is a strict offline aggregate-v1 validator. Its field
allowlist, byte cap, safe integer range, bucket count, calendar month checks and
summary invariants match Slaymish/astro-blog's src/server/codexReports.ts.
tests/fixtures/report-validation.json is mirrored byte-for-byte in both repos;
run each repository's tests when changing that contract. Reports with no usable
sessions are diagnostic exports, not valid contributions.

The skill requires explicit consent before reading personal history and never
uploads automatically. Website authentication, storage consent, attribution,
moderation, deduplication and deletion belong to Slaymish/astro-blog. Identity is
verified through GitHub OAuth on the website, never entered into an exported
report. No GitHub credentials or usernames belong in report files.

The website stores at most one complete snapshot per verified numeric GitHub ID.
Changed snapshots replace old data and return to private review. Public profiles
require a reviewed, unexpired report, a separate explicit opt-in and at least
five eligible contributors. Withdrawal removes report and profile fields, while
an empty pseudonymous marker prevents stale updates from restoring withdrawn
data. Reports expire after 90 days. No public usage buckets or statistical
estimates are published by this contributor flow.

The exporter cannot determine paid tier, quota/reset windows, prices, credits or
active coding hours from token counts. Aggregate reports are not guaranteed
anonymous, and multiple GitHub accounts are not proof of independent people.
Production submissions remain a separate launch decision after real GitHub and
Netlify tests; local validation or mocked tests do not prove deployed operation.
