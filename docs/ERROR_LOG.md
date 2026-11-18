# Error analysis log

How each problem was found, what was inspected, what was changed, and whether the change caused another error. Synthetic data only.

| # | Observed error | What was inspected | Fix | Re-run and regression check |
|---|---|---|---|---|
| 1 | Privacy leak: with no consent, the page could still reveal that a partner had an uncertain variant (384 of 5,000 random trials) | The reasons list built when consent was missing | Stopped adding the uncertain-variant reason in the no-consent branch | 0 of 5,000 trials leak |
| 2 | The same leak came back when the rules were copied into the backend (19 of 20 checks) | Diff of the copied rules against the original | Removed the re-introduced line | 20 of 20 checks |
| 3 | Reading grade of one message rose to 8.2 (limit 8) after adding "genetic counselor or doctor" | Sentence length and syllable counts | Scored four rewordings and kept the one that passed (7.8) | 21 of 21 checks |
| 4 | Continuous integration failed: plain `pytest` could not import the app, while `python -m pytest` passed locally | Reproduced with plain `pytest` in a clean environment | Added `pytest.ini` with `pythonpath = .` | Passes in a clean virtual environment. Confirm the green check on GitHub Actions. |
| 5 | One partner's distress flag appeared as "Review recommended" in the other partner's view | The couple-level flag and the view logic | Stored the flag per partner; only the setter and staff see it | New API test; 17 tests pass |
| 6 | An intake brief stayed on screen after the answers changed, so it disagreed with the page | The sequence of requests in the server log | The brief is cleared when answers change | Checked by hand |
| 7 | The README said every tab runs on the API; only some do | Which tabs call the API | Corrected the sentence | Reviewed |
| 8 | The language check passed on the app's own text but caught only 1 of 8 unsafe sentences written separately | A held-out set of unsafe and safe sentences | Added pattern groups (advising against, ending a relationship, false certainty, blame words) | 8 of 8 on that set, but it had guided the patch. A fresh set then caught 6 of 8 (0 false positives); the 2 misses were patched. Both sets are now regression tests. |
| 9 | The emergency-wording detector missed "I am thinking of ending my life" because the pattern said "end my life" | The held-out phrases added after the first version | Matched "end" and "ending" | Re-run: listed phrases caught, 0 benign questions flagged. Indirect wording (for example "I feel like I can't go on") is still not caught, and is listed as a known gap. |

## What this tells us
- Problems 1, 2, 3 and 8 were found by the test harness, not by reading the code.
- The language check is a keyword safety net, not a classifier. Both test sets were written by the author, so real recall on unseen phrasing is probably lower. Human and native-speaker review are still needed.
- Test sentences are kept separate from the text used to build the rules, and each fix is followed by a re-run of the affected cases.
