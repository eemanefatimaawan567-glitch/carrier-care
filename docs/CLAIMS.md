# Claims audit

Every claim made about this project, with how it is checked. Synthetic data only. Education and decision support, not clinical advice.

## Claims we make
| Claim | How it is checked |
|---|---|
| No language model writes or computes risk text | Inspection: no model call anywhere in the repository. All user-facing text is in `backend/app/engine.py` and `frontend/index.html` |
| For an applicable autosomal recessive carrier couple: 25% unaffected non-carrier, 50% unaffected carrier, 25% affected per pregnancy; uncertain variants never get a risk figure; relatedness is not an input to the risk engine | `eval/run_eval.py` (engine checks) |
| A couple view is only produced for genes both partners allow; genes outside the agreed scope never influence the output | 5,000-trial randomized check in `eval/run_eval.py`; `test_granular_consent_scope` |
| With no consent, the shared view is independent of both partners' results; a single carrier's status is never revealed | Two 5,000-trial randomized checks; API tests |
| One partner's distress flag is not visible to the other partner | `test_distress_is_private_to_the_partner_who_flags` |
| Partner tokens are stored as SHA-256 hashes; staff tokens are compared in constant time | `test_partner_tokens_hashed_at_rest_and_headers`; code inspection |
| The audit ledger is append-only in the application, hash-chained, and never stores genetic results | `test_ledger_has_no_results_and_detects_tampering` |
| "Delete my data" removes that partner's results and family history rows from the database | `test_privacy_dashboard_and_deletion` |
| Roles are enforced (partner, counselor, coordinator) | `test_roles_and_isolation` and related tests |
| App text contains no phrase from the unsafe-phrase list and only the approved percentages (25, 50) | Language checks in `eval/run_eval.py`. The list is a keyword safety net: on separately written sentences it first caught 1 of 8, then 6 of 8 on a fresh set; see `docs/ERROR_LOG.md` |
| Key English sentences read at grade 8 or below | Readability checks in `eval/run_eval.py` (Arabic is not measured) |
| The FHIR-style export contains no genetic results | `test_fhir_has_no_results_and_is_staff_only` (not validated against FHIR profiles) |

## Claims we do not make
- **Audited or clinically validated templates.** No genetic counselor or clinician has reviewed the content. A molecular geneticist checked five statements for facts and clarity only.
- **Memory purge.** Withdrawing consent locks the couple view. Results stay in the database until the person uses "Delete my data". Nothing is held only in memory.
- **Cryptographic matching, zero-knowledge proofs or private set intersection.** Matching runs in the server's rules engine after both partners consent, so the server operator can see everything. Real PSI is future work.
- **Database-level intersection queries.** The intersection is computed in Python, not in SQL.
- **Any integration with, or formal submission to, Malaffi, a hospital or a university program.** None exists. Individuals were contacted informally.
- **A tokenized referral protocol.** Not implemented. The app tracks referral stages and offers a FHIR-style export with pseudonymous IDs.
- **Measured comprehension, counseling uptake or time to referral.** The prototype can record anonymous quiz scores and ledger timings (shown as demo data). No study has been run.
- **Real patient data or regulatory approval.** None. A real deployment would need legal review under UAE and Abu Dhabi health-data rules (for example Federal Law No. 2 of 2019 on ICT in health fields; verify current requirements).

- **A crisis or emergency service.** The tool shows a fixed emergency message when keywords appear in the free-text box, and a standing notice in the footer. The keyword check misses indirect wording, and no staff queue is monitored in real time.

## Known limitations that remain
- The ledger detects edits but not deletion of the newest records or a full rewrite by a database administrator. Plan: anchor the latest hash outside the database.
- Staff tokens are shared secrets without per-case assignment or expiry.
- No rate limiting on open endpoints (case creation, quiz).
- Database is unencrypted SQLite. Fonts load from Google Fonts.
- When the backend is unreachable, the browser falls back to a local copy of the rules, which does not apply the per-partner distress rule.

## Outreach is not verification

- Asif Jamal provided five yes/no factual/clarity responses and consented to acknowledgement; this was not full clinical review.
- An additional contact provided informal comments about counseling and confidentiality, not a clinical assessment of the software.
- Contacting genetics clinics or sending LinkedIn requests does not mean a professional has reviewed the application, accepted a pilot, or endorsed it.
- The current business pricing model is illustrative and has not been validated by paying customers.
