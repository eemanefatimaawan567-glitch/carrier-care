# Deployment

All data in this project is synthetic. Do not run it with real patient data.

## Option A: local
```
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload      # http://localhost:8000
```

## Option B: Docker
```
docker compose up --build          # http://localhost:8000
```
Optional `.env` file next to `docker-compose.yml` (not committed):
```
COUNSELOR_TOKEN=choose-a-long-random-string
COORDINATOR_TOKEN=choose-another-long-random-string
CARRIER_ENV=production
```
With `CARRIER_ENV=production` the app refuses to start if the demo tokens are still in use.

## Option C: current public Render synthetic demo

- Public URL: https://amanah-genomics-demo.onrender.com/
- Health check: https://amanah-genomics-demo.onrender.com/health
- GitHub source: https://github.com/eemanefatimaawan567-glitch/carrier-care
- The service runs on a Render free instance. It may cold-start after inactivity and **does not provide clinical-grade uptime or durable synthetic case storage**.

Steps to reproduce on a compatible host (verify provider details):
1. Create a new web service from the GitHub repository, using the `Dockerfile`.
2. Set environment variables `COUNSELOR_TOKEN`, `COORDINATOR_TOKEN` (and `CARRIER_ENV=production` if you set real tokens).
3. Use `/health` as the health-check path.
4. Open the service URL. Free tiers may sleep when idle and may reset the database on restart. That is acceptable for synthetic data.

Staff tokens are configured through environment variables; do not post real values or include them in screenshots. A public synthetic demonstration must never be used with real patient data. Avoid relying on example/default tokens for any production setting.

## Production readiness checklist
| Item | Status |
|---|---|
| Automated tests and CI on every push | Done |
| Evaluation harness (privacy, language, readability) | Done |
| Role checks and tamper-evident ledger | Done |
| Dockerfile and public Render deployment | Implemented for synthetic demonstration; latest commit still needs a successful redeploy check |
| Named staff accounts, token expiry, HTTPS enforcement | Planned |
| Encrypted storage, backups, monitoring | Planned |
| Rate limiting | Planned |
| Real private set intersection | Future work |
| Independent security review | Future work |
| Clinical and native-speaker review of content | Pending |

## Judge verification checklist

1. Verify the most recent commit reaches **Live** in Render Deploys.
2. Open the public homepage and `/health` (the free instance may sleep when idle).
3. Visit `/advanced.html?view=server` and run all three independent synthetic consent checks; record actual result.
4. Open Counselor and Coordinator workspaces with their separate configured tokens. Confirm role visibility, staff queue, and referral-stage actions. Do not expose tokens.
5. Switch `?lang=ar` and `?lang=en` on the homepage and advanced workspace; inspect synthetic examples, navigation, and safety notices.
6. Check the GitHub Actions run for the **same code revision** as the public deployment; attach a dated screenshot or URL to the submission.

## Architecture and scalability roadmap (proposed, not deployed)

| Area | Current demo | Production requirement / proposal |
|---|---|---|
| Hosting | Containerized FastAPI on Render free service | Managed reliable hosting, monitoring and controlled rollouts |
| Storage | SQLite with ephemeral filesystem | Encrypted managed PostgreSQL, backups, restore drills, migration plan |
| Authentication | Role-specific demo tokens | Individual identities, token expiry/rotation, robust access controls |
| Privacy | App-enforced consent for scoped synthetic cases, hash-chained ledger | Security assessment, key management, audited retention and independent privacy review |
| Availability | Free tier may sleep; no SLA claimed | Availability targets, health monitoring, incident response, load testing |
| Interoperability | FHIR-style export demonstration | Conformance testing and approved provider integrations (none currently active) |
| Clinical readiness | Educational synthetic test scenarios | Qualified clinical and Arabic-language review, institution-approved pilot and regulatory assessment |

**Do not describe any planned item as an implemented feature, completed partnership, or clinically validated service.**
