# Amanah Genomics — Patient flow & privacy verification update

1. Primary desktop navigation is now a **five-step patient journey**, followed by consent/privacy. Risk Curve and Punnett Square are preserved under **Explore more learning tools**.
2. **Research & staff demos** is a separate collapsed section with clear non-clinical notices on technical, staff and pilot pages. This is a **UI distinction**, not an authentication layer; staff API authorization remains enforced by FastAPI.
3. The **Live backend** screen includes a **Run consent safety checks** button. It creates a new synthetic couple and performs actual API calls verifying one-sided consent locks comparison, dual consent unlocks permitted matching, and withdrawal relocks comparison. The display reports pass/fail only after real responses.
4. Added a targeted FastAPI regression test covering consent from both partner views. The previous tests are preserved.
5. Never use real patient data; this is not clinical or security certification.
