# Amanah Genomics — Connected Experience

## Changes
- Desktop: permanent navy sidebar grouped by journey, genetics tools, privacy and business.
- Mobile/tablet: existing floating All Tools menu retained so all pages remain reachable.
- The Amanah logo remains a clickable home link.
- Toolkit now uses the same navy/teal brand family as the website.
- Private Match includes three one-click synthetic scenario shortcuts and explicit teaching-only disclosure.
- Current tool is highlighted and the workspace breadcrumb updates.
- Homepage includes a prominent Open Workspace action.
- No original pages, API routes, risk visuals, privacy logic, quizzes or counseling modules intentionally removed.

## Running
```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
Visit http://127.0.0.1:8000 and http://127.0.0.1:8000/advanced.html.

## Safety
Public demonstrations should use fictional synthetic data only. Guided and toolkit demos are not substitutes for clinical counseling or certified privacy controls.
