# Privacy and measurement boundaries

The exporter runs locally and never uses the network. It reads local Codex JSONL history but **does not export** conversation text, tool commands, paths, session IDs, filenames, timestamps more precise than UTC month, or repository names. It exports monthly model buckets and cumulative token totals.

**Privacy is not guaranteed:** a rare model, unusually high token usage or an isolated month can still make a contributor recognisable. Review the entire JSON before sharing. Contributions and public attribution must be separate opt-in decisions. Do not automatically upload the file.

The collector does not know actual subscription quotas, credit charges, paid tier, five-hour resets, daily coding time, or elapsed active work. It must not present token counts as equivalent to those measures. The model recorded from a turn context is an approximate session label; sessions switching models may be mislabelled. Session token snapshots may be missing or incompatible across Codex versions. A model-accurate future exporter should partition usage by turn if source telemetry supports it.

No ingestion endpoint exists yet. Before launching one, add strict schema validation, abuse/rate limits, aggregate-only persistence, contributor withdrawal, sample-size suppression, retention policy and independent privacy review.
