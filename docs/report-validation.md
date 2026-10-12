# Report validation

Validate a local export before sharing:

```sh
python3 scripts/validate_report.py codex-usage-report.json
python3 -m unittest discover -s tests -v
```

Validation is strict: only the documented v1 aggregate fields are accepted. Extra fields (including accidental private content), negative/boolean token values, duplicate month/model buckets, inconsistent counts, invalid months, unsupported versions and files larger than 256 KB are rejected.

This is **not** an upload endpoint or proof of anonymity. A malicious submitter can fabricate plausible totals. Public aggregation will need contributor-level deduplication, abuse prevention, privacy thresholds, retention and withdrawal controls. A report cannot measure five-hour quotas or active coding time.

## Website contribution contract

The report JSON remains exactly the offline aggregate-v1 schema. Do not add a
GitHub username, ID, profile image, consent flag, review status or credentials.
GitHub identity is verified separately by the website, and report sharing and
public attribution are separate decisions. Each account has one current full
snapshot; updated data replaces it and requires review again. Identical reports
from different verified accounts are independent, without proving that the
accounts represent independent people.

The website API envelope is report, optIn (an explicit boolean) and revision
(the account version obtained after sign-in). Its account-scoped handlers also
require a session cookie, exact same-site Origin and a CSRF token. There is no
upload command in this repository, and running the skill or validator never
submits a report. Withdrawal/deletion and opt-out are managed after signing in
to the website, including while new submissions are paused.

Shared synthetic validation cases live in tests/fixtures/report-validation.json
and are mirrored in Slaymish/astro-blog. The validators reject year zero,
trailing newlines in labels, booleans masquerading as integers, fewer snapshots
than usable sessions, impossible file counts and unsafe numeric sums. Run both
suites for any contract change.

Before launch, real GitHub OAuth, Netlify conditional writes, retention and
withdrawal still need deployment verification. Automated tests do not prove
end-to-end production functionality. No public statistical dataset or quota
calibration is implemented by this flow.
