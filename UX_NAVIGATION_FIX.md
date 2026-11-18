# Navigation improvement — Amanah Genomics

## Fixed
- Amanah branding on the advanced tools page now navigates to the website homepage.
- Both pages include a persistent **All tools** menu, accessible without returning to the toolkit directory.
- Advanced tool buttons navigate within the current page without reload and preserve the current tool in the URL.
- Buttons and links are keyboard accessible; Escape closes the navigation panel.
- Existing animations, risk visuals, quizzes, consent logic, counselor workflow and backend are unchanged.

## Run locally
```bash
cd /Users/gyn/Downloads/Amanah_Genomics_UX_Navigation_Fixed/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
Visit http://127.0.0.1:8000 and hard refresh (Cmd+Shift+R).

Use synthetic demo data only. This is not clinically validated.
