# Evaluation report
Generated 2026-11-17 on synthetic data. 37/37 checks passed.

| Result | Check | Detail |
|---|---|---|
| PASS | Carrier x carrier = 25/50/25 |  |
| PASS | Carrier x non-carrier: no affected child |  |
| PASS | Probabilities always sum to 1 |  |
| PASS | VUS never becomes a risk figure |  |
| PASS | Relatedness is not an input to the risk engine |  |
| PASS | No-consent view is independent of both partners' results (5000 trials) | 0 leaking trials |
| PASS | Unilateral carrier status is never revealed (5000 trials) | 0 trials |
| PASS | Only shared-gene IDs appear in output | 0 trials |
| PASS | Genes outside the agreed scope never influence output (5000 trials) | 0 trials |
| PASS | No directive, stigmatizing or coercive phrases (EN+AR) | [] |
| PASS | Only approved percentages appear in text | found [25] |
| PASS | No success metric based on cancelled marriages |  |
| PASS | Arabic has every English message key |  |
| PASS | Every escalation produces a counselor message |  |
| PASS | Language lint regression set heldout_v1.json: all unsafe caught, no safe flagged | first held-out set: 1 of 8 unsafe caught before the first patch; now missed=0, false positives=0 |
| PASS | Language lint regression set heldout_v2.json: all unsafe caught, no safe flagged | fresh set: 6 of 8 caught before the second patch; now missed=0, false positives=0 |
| PASS | Benchmark case: Both carry HBB, both consent | as expected |
| PASS | Benchmark case: Only one partner carries (no match) | as expected |
| PASS | Benchmark case: Both carry HBB but Partner B withheld consent | as expected |
| PASS | Benchmark case: Both carry HBB and GJB2, scope limited to GJB2 | as expected |
| PASS | Benchmark case: Uncertain variant in A, none in B | as expected |
| PASS | Benchmark case: Uncertain variant outside the agreed scope | as expected |
| PASS | Benchmark case: Both have an uncertain variant in the same gene | as expected |
| PASS | Benchmark case: No carriers, distress flagged | as expected |
| PASS | Benchmark case: Related partners, no shared carrier | as expected |
| PASS | Benchmark case: Both consented but agreed genes do not overlap | as expected |
| PASS | Benchmark case: Severe gene SMN1, both carry, related | as expected |
| PASS | Benchmark case: A carries one gene, B has an uncertain variant in another | as expected |
| PASS | Benchmark case: Arabic: both carry CFTR | as expected |
| PASS | Emergency detector: catches listed phrases and flags no benign question | missed=0, false positives=0; known gaps (not caught): 3 of 3 |
| PASS | Reading grade <= 8: couple result | grade 3.4, ease 82.9 |
| PASS | Reading grade <= 8: no match | grade 7.4, ease 54.7 |
| PASS | Reading grade <= 8: related | grade 7.8, ease 52.6 |
| PASS | Reading grade <= 8: uncertain | grade 6.1, ease 63.8 |
| PASS | Reading grade <= 8: family message | grade 7.2, ease 57.1 |
| PASS | Reading grade <= 8: level Simple | grade 3.1, ease 93.3 |
| PASS | Reading grade <= 8: level Standard | grade 5.9, ease 70.8 |

## Readability (English)
| Text | FK grade | Reading ease |
|---|---|---|
| couple result | 3.4 | 82.9 |
| no match | 7.4 | 54.7 |
| related | 7.8 | 52.6 |
| uncertain | 6.1 | 63.8 |
| family message | 7.2 | 57.1 |
| level Simple | 3.1 | 93.3 |
| level Standard | 5.9 | 70.8 |
| level Clinical | 13.3 | 16.1 |

## Arabic length stats (no validated Arabic readability formula is used)
| Message | Words per sentence | Chars per word |
|---|---|---|
| sh | 6.3 | 4.8 |
| none | 8.0 | 4.4 |
| rel | 9.0 | 5.3 |
| vus | 10.3 | 4.2 |
| lock | 5.0 | 6.0 |
| esc | 8.0 | 5.2 |

## What a pass means
A full pass shows the rules behave as specified on the cases the author thought of, including missing consent, uncertain variants, out-of-scope genes, distress and Arabic output. It is not evidence of clinical accuracy or of safety on unseen inputs. Calibration is not applicable: there is no probabilistic model, and the risk figures are fixed inheritance ratios.

## Language lint is a keyword safety net, not a classifier
On sentences written separately from the app text, the first lint caught 1 of 8 unsafe sentences. After a patch it caught 6 of 8 on a fresh set, then both sets became regression tests. Both sets were written by the author, so real recall on unseen phrasing is likely lower. Human and native-speaker review are still needed.

## Not yet measured
- Real comprehension (pre/post quiz) needs human participants. Do not simulate it.
- Counseling uptake and time to referral need a pilot or a clearly labeled simulation.
- Equity across languages beyond EN/AR.