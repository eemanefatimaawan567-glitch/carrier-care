# Submission claims alignment — 17 November 2026

This document separates engineering evidence, demonstrations and unverified plans. It is an internal communication audit, **not** an independent medical, security or deployment certification.

| Topic | Safe claim today | Evidence / boundary |
|---|---|---|
| Core engine | Built deterministic educational rules for selected recessive carrier cases | `backend/app/engine.py`; not comprehensive genetic interpretation |
| Consent | Backend enforces per-gene permission checks for shared result workflows | `backend/tests/test_api.py`, `docs/CLAIMS.md`; browser-only guided consent is a simulation |
| Test results | 18/18 backend tests reported passing; 37/37 synthetic evaluation checks reported passing | Dated local report, rerun after final changes |
| Random trials | Specific synthetic privacy invariants checked across 5,000 random trials per applicable test | `backend/eval/eval_report.md`; not 5,000 real patients |
| Audit | Hash-chained application-level audit log | Not external notarization or resistance to an all-powerful database administrator |
| Risk graphics / quiz | Frontend includes graphs, inheritance illustrations and educational self-checks | Not measured improvements in patient understanding |
| Arabic | English/Arabic educational content and RTL UI support | Not independently clinically translated or certified; some technical UI text may not be localized |
| Genetics review | Five selected statements checked for accuracy and clarity, with permission for acknowledgement | Not complete clinical validation or endorsement |
| Counseling | Demonstration queue, intake brief and referral-stage tracking | No actual accredited counselor booking or live referral |
| Health-system integration | FHIR-style export for hypothetical future interoperability | No validated FHIR profile; no Malaffi or UAE Pass connection |
| Commercialization | B2B licensing hypothesis and illustrative AED pricing model | No customers, contracts, pilots or validated willingness-to-pay |
| Deployment | Docker and deployment instructions present | Public HTTPS production instance has not been independently confirmed |
| Security | Prototype-specific controls including server-side consent and hashed partner tokens | No independent penetration test, certified compliance or production assurances |

## Phrases to avoid until independently proven

- “Clinically validated”, “doctor-approved”, “medically certified Arabic”
- “Integrated with Malaffi/UAE Pass”
- “Military-grade encryption”, “zero knowledge”, “fully anonymous records”
- “Enterprise-ready”, “HIPAA/DOH compliant”
- “A clinical review is scheduled” (unless a reviewer and date have been confirmed)
- “Improves comprehension by X%” without real participant evaluation
- “Clinically reduces inherited disease incidence” (not demonstrated)

## Safe submission paragraph

> Amanah Genomics is a bilingual, consent-first educational prototype for selected inherited-disease carrier-screening scenarios. It combines deterministic explanatory rules, a backend permission-gated matching workflow, visual risk education, comprehension self-checks, and a demonstration counseling handoff. In the latest recorded local checks, 18 automated tests and 37 synthetic evaluation checks passed, including randomized privacy tests. An external molecular-genetics contact checked five selected statements for facts and clarity. The prototype has not undergone formal clinical validation, real-patient usability trials, independent Arabic clinical review, security certification, or live hospital integration. Institutional piloting and integration remain proposed future steps.

## Remaining checks before submission

1. Confirm 18/18 and 37/37 in the exact final GitHub commit; archive terminal output.
2. Search README, all pitch slides, video captions and Hack2skill text for absolute phrases like “guarantees”, “validated”, “integrated”, “certified”.
3. Inspect the live deployed UI to ensure its consent simulation is never mistaken for server security.
4. Confirm any external reviewer role and permission; distinguish contacted, replied, and actually reviewed.
5. Check every screenshot or business calculation is labeled synthetic / illustrative where necessary.
