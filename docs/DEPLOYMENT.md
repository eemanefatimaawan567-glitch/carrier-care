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

## Option C: free cloud host (for a public synthetic demo)
Steps are typical for hosts such as Render, Railway or Fly.io; check the host's current documentation.
1. Create a new web service from the GitHub repository, using the `Dockerfile`.
2. Set environment variables `COUNSELOR_TOKEN`, `COORDINATOR_TOKEN` (and `CARRIER_ENV=production` if you set real tokens).
3. Use `/health` as the health-check path.
4. Open the service URL. Free tiers may sleep when idle and may reset the database on restart. That is acceptable for synthetic data.

Public demo note: if you keep the demo tokens (`counselor-demo`, `coordinator-demo`) so judges can sign in as staff, anyone can. That is acceptable only because the data is synthetic.

## Production readiness checklist
| Item | Status |
|---|---|
| Automated tests and CI on every push | Done |
| Evaluation harness (privacy, language, readability) | Done |
| Role checks and tamper-evident ledger | Done |
| Container image and compose file | Done (not yet run on a hosting provider by the author) |
| Named staff accounts, token expiry, HTTPS enforcement | Planned |
| Encrypted storage, backups, monitoring | Planned |
| Rate limiting | Planned |
| Real private set intersection | Future work |
| Independent security review | Future work |
| Clinical and native-speaker review of content | Pending |
