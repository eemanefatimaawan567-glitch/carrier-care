# Amanah Genomics — public synthetic demo deployment

## Before deployment
- Use **synthetic data only**. Never enter identifiable patient genetic information.
- This is an educational prototype, **not** a clinical service or production-grade healthcare deployment.
- Public free-tier services can sleep, restart, and lose local SQLite data.
- The deployed server serves both `frontend/index.html` and FastAPI at the SAME origin.

## Steps
1. Upload the contents of this folder (not the outer ZIP folder) to GitHub repository `carrier-care`, so `Dockerfile`, `render.yaml`, `frontend/`, and `backend/` are at the repository root.
2. Confirm GitHub Actions passes on the latest commit.
3. Open Render → New → Blueprint and select that repository.
4. Render will read `render.yaml`: Docker runtime, free plan, `/health`, and generated staff tokens.
5. Review the settings and deploy. Copy the HTTPS `*.onrender.com` URL.
6. Check `<URL>/health` returns `{"ok":true}` and `<URL>/` opens the home page.
7. Open `<URL>/advanced.html`. Test graph, quiz, English/Arabic, a successful dual-consent case and refused consent case.
8. Review the Render logs for errors; do not claim complete deployment until these checks pass.

## Important
The counselor and coordinator secrets are randomized in Render. Do not commit them to GitHub or share them as public demo credentials.
For a public walkthrough, use the partner synthetic scenarios; staff access requires separately held tokens.
A free Render container has ephemeral storage, so records will not persist reliably.
If a deployment does not support persisted `/data` storage, use it only as a temporary synthetic demonstration.

## App config
- `CARRIER_DB` defaults to `/data/carrier.db` from the Dockerfile.
- `CARRIER_ENV=production` enforces non-demo staff tokens.
- Docker command starts `uvicorn app.main:app` on Render's `${PORT}`.
