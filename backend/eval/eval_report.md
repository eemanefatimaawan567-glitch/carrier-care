# Evaluation report
Generated 2026-10-22 on synthetic data. 21/21 checks passed.

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
| sh | 6.0 | 4.7 |
| none | 5.5 | 4.9 |
| rel | 7.5 | 5.3 |
| vus | 8.7 | 4.5 |
| lock | 5.0 | 6.0 |
| esc | 8.0 | 5.2 |

## Not yet measured
- Real comprehension (pre/post quiz) needs human participants. Do not simulate it.
- Counseling uptake and time to referral need a pilot or a clearly labeled simulation.
- Equity across languages beyond EN/AR.