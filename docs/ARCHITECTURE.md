# Architecture

```mermaid
flowchart LR
  P[Partner A / B browser] -->|own token| API
  S[Counselor / Coordinator browser] -->|staff token| API
  subgraph Server
    API[FastAPI] --> R[Rules engine and approved text]
    API --> DB[(SQLite: couples, tokens, results, history, quiz)]
    API --> L[(Hash-chained ledger: consent, views, referral events)]
  end
  API --> F[FHIR-style export: no genetic results]
```

## Consent-gated match

```mermaid
sequenceDiagram
  participant A as Partner A
  participant B as Partner B
  participant S as Server
  participant C as Counselor
  A->>S: store own results, consent for chosen genes
  B->>S: store own results, consent for chosen genes
  A->>S: request couple view
  S->>S: scope = genes both partners allow
  S-->>A: output only for shared carrier genes in scope
  Note over S: A genes outside scope never affect output
  S->>C: SBAR handoff and queue priority (if review is triggered)
  S->>S: append event to hash-chained ledger
```

## Where a health system would connect later
- Results would arrive from an accredited laboratory (today: entered by hand, synthetic).
- Referrals would leave as FHIR resources (today: FHIR-style export only, nothing transmitted).
- No integration with any health information exchange exists.
