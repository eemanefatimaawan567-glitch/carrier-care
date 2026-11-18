# Threat model (prototype, synthetic data)

Assets: partner results, consent state, family history, audit ledger, access tokens.
Actors: partner, other partner, counselor, coordinator, outsider, server operator.

| # | Threat | Mitigation in the prototype | Tested? | Residual risk and plan |
|---|---|---|---|---|
| 1 | A partner learns the other's single-carrier or uncertain result | Server-side gating, per-gene scope; output never depends on genes outside scope | Yes: 5,000 randomized trials each for no-consent, unilateral carrier and scope | The server operator can see everything. Plan: real private set intersection with a vetted library |
| 2 | Revoked consent still exposes results | Consent is the latest ledger event; view locks immediately | Yes | None known |
| 3 | Staff see more than needed | Role checks; counselor sees handoff and ledger; coordinator sees stage and ledger | Yes: 403 checks | Staff tokens are shared secrets with no per-case assignment. Plan: named accounts, assignment, expiry |
| 4 | Token guessing or theft | Partner tokens are 24 random bytes; tokens never logged in the ledger | Partly | Staff tokens are static. Plan: expiry, rotation, HTTPS only |
| 5 | Ledger tampering | SHA-256 hash chain; verify endpoint | Yes: an edited record breaks the chain | An administrator could rewrite the whole chain. Plan: anchor the latest hash outside the database |
| 6 | Re-identification from the brief or case ID | Pseudonymous case reference; no names or ID numbers collected | Yes: no results in ledger, FHIR or brief | A counselor still needs to identify the patient. Documented as pseudonymous, not anonymous |
| 7 | Script injection or SQL injection | Output is escaped in the UI; SQL is parameterized | Partly | Plan: security review and a content-security policy |
| 8 | Abuse of open endpoints (case creation, quiz) | Input validation | No | No rate limiting. Plan: rate limits and captcha for public hosting |
| 9 | Data at rest readable | None (plain SQLite file) | No | Plan: encrypted storage and backups |
| 10 | Third-party fonts reveal visitor IPs | None | No | Plan: self-host fonts |
| 11 | Users misread results or feel pushed | Plain language, "a chance, not a diagnosis", non-directive wording, referral to a genetic counselor or doctor | Yes: language lint and readability checks | Needs clinician and native-speaker review |

Out of scope: real patient data, clinical validation, integration with any health system.
