import os, json, secrets, hashlib, hmac
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from . import db, engine as E
db.init()
app = FastAPI(title="Consent-first carrier care (prototype)")
COUNSELOR = os.environ.get("COUNSELOR_TOKEN", "counselor-demo"); COORD = os.environ.get("COORDINATOR_TOKEN", "coordinator-demo")
if os.environ.get("CARRIER_ENV") == "production" and ("counselor-demo" in (COUNSELOR,) or "coordinator-demo" in (COORD,)): raise RuntimeError("Set COUNSELOR_TOKEN and COORDINATOR_TOKEN before running with CARRIER_ENV=production")
STAGES = ["Result issued", "Counselor notified", "Counseling completed", "Confirmatory testing", "Reproductive-genomics service (if chosen)"]
class NewCouple(BaseModel): related: bool = False
class Results(BaseModel): results: dict[str, str]
class Consent(BaseModel):
    share: bool
    genes: list[str] | None = None
class Brief(BaseModel): questions: str = ""
class Flags(BaseModel): distress: bool
def auth(c, cid, tok):
    if hmac.compare_digest(tok.encode(), COUNSELOR.encode()): return "counselor"
    if hmac.compare_digest(tok.encode(), COORD.encode()): return "coordinator"
    r = c.execute("select role from tokens where token=? and couple_id=?", (hashlib.sha256(tok.encode()).hexdigest(), cid)).fetchone()
    if not r: raise HTTPException(403, "forbidden")
    return r["role"]
def partner_only(c, cid, tok):
    role = auth(c, cid, tok)
    if role not in ("A", "B"): raise HTTPException(403, "partners only")
    return role
def distress_for(c, cid, viewer):
    rows = c.execute("select partner, distress from flags where couple_id=?", (cid,)).fetchall()
    return any(r["distress"] for r in rows if viewer is None or r["partner"] == viewer)
def compute(c, cid, lang="en", viewer=None):
    cp = c.execute("select * from couples where id=?", (cid,)).fetchone()
    if not cp: raise HTTPException(404, "not found")
    R = {p: c.execute("select genes from results where couple_id=? and partner=?", (cid, p)).fetchone() for p in "AB"}
    if not all(R.values()): raise HTTPException(409, "waiting for both partners' results")
    A, B = (json.loads(R[p]["genes"]) for p in "AB"); ga, gb = db.consent_genes(c, cid, "A"), db.consent_genes(c, cid, "B"); scope = ga & gb
    v = E.couple_view(A, B, bool(ga), bool(gb), bool(cp["related"]), distress_for(c, cid, viewer), lang, scope=scope)
    return v, bool(cp["related"]), bool(scope)
@app.post("/couples")
def create(b: NewCouple):
    cid = secrets.token_hex(6); c = db.conn(); c.execute("insert into couples(id,related) values(?,?)", (cid, int(b.related))); out = {"couple_id": cid}
    for p in "AB":
        t = secrets.token_urlsafe(24); c.execute("insert into tokens values(?,?,?)", (hashlib.sha256(t.encode()).hexdigest(), cid, p)); out["token_" + p.lower()] = t
    db.log(c, cid, "system", "couple_created"); c.commit(); return out
@app.put("/couples/{cid}/results")
def put_results(cid: str, b: Results, x_token: str = Header()):
    c = db.conn(); p = partner_only(c, cid, x_token)
    if set(b.results) != set(E.GENES) or any(v not in ("0", "1", "2") for v in b.results.values()): raise HTTPException(422, "invalid panel")
    c.execute("insert or replace into results values(?,?,?)", (cid, p, json.dumps(b.results))); db.log(c, cid, p, "results_stored"); c.commit(); return {"ok": True}
@app.put("/couples/{cid}/consent")
def put_consent(cid: str, b: Consent, x_token: str = Header()):
    c = db.conn(); p = partner_only(c, cid, x_token)
    if b.share and b.genes is not None and (not b.genes or set(b.genes) - set(E.GENES)): raise HTTPException(422, "invalid genes")
    db.log(c, cid, p, "consent", {"share": b.share, "genes": sorted(b.genes) if (b.share and b.genes) else None}); c.commit(); return {"share": b.share}
@app.put("/couples/{cid}/flags")
def put_flags(cid: str, b: Flags, x_token: str = Header()):
    c = db.conn(); p = partner_only(c, cid, x_token); c.execute("insert or replace into flags values(?,?,?)", (cid, p, int(b.distress))); db.log(c, cid, p, "flag", {"distress": b.distress}); c.commit(); return {"ok": True}
@app.get("/couples/{cid}/view")
def view(cid: str, lang: str = "en", x_token: str = Header()):
    c = db.conn(); p = partner_only(c, cid, x_token); v, rel, both = compute(c, cid, lang, viewer=p)
    db.log(c, cid, p, "view", {"escalate": v["escalate"]}); c.commit()
    return {"text": v["text"], "escalate": v["escalate"], "genes_shown": v["genes_shown"], "reasons": v["reasons"], "referral_stage": STAGES[min(db.stage(c, cid), 4)] if v["escalate"] else None}
@app.get("/couples/{cid}/staff-role")
def staff_role(cid: str, x_token: str = Header()):
    c = db.conn()
    role = auth(c, cid, x_token)
    if role not in ("counselor", "coordinator"):
        raise HTTPException(403, "staff only")
    return {"role": role}

@app.get("/couples/{cid}/handoff")
def handoff(cid: str, x_token: str = Header()):
    c = db.conn(); role = auth(c, cid, x_token)
    if role != "counselor": raise HTTPException(403, "counselors only")
    v, rel, both = compute(c, cid); db.log(c, cid, "counselor", "handoff_viewed"); c.commit(); text = E.sbar(v, rel, both)
    rows = c.execute("select * from history where couple_id=?", (cid,)).fetchall()
    pick = lambda val: {p: i for p, i in ((r["partner"], [E.HISTORY[k] for k, v in json.loads(r["answers"]).items() if v == val]) for r in rows) if i}
    yes, unsure = pick("yes"), pick("unsure")
    if yes:
        if text.startswith("No handoff needed."): text = "S: Screening results alone do not trigger review. Family history was reported.\nR: Genetic counseling visit."
        text += "\nFamily history (self-reported): " + "; ".join(f"Partner {p}: {', '.join(i)}" for p, i in yes.items())
    if unsure: text += "\nFamily history, not sure about: " + "; ".join(f"Partner {p}: {', '.join(i)}" for p, i in unsure.items())
    return {"sbar": text}
@app.post("/couples/{cid}/referral/advance")
def advance(cid: str, x_token: str = Header()):
    c = db.conn(); role = auth(c, cid, x_token)
    if role != "coordinator": raise HTTPException(403, "coordinators only")
    v, _, _ = compute(c, cid)
    if not v["escalate"]: raise HTTPException(409, "no referral needed")
    if db.stage(c, cid) >= 4: raise HTTPException(409, "pathway complete")
    db.log(c, cid, "coordinator", "referral_advance"); c.commit(); return {"stage": STAGES[db.stage(c, cid)]}
@app.get("/couples/{cid}/audit")
def audit(cid: str, x_token: str = Header()):
    c = db.conn(); role = auth(c, cid, x_token)
    if role not in ("counselor", "coordinator"): raise HTTPException(403, "staff only")
    rows = [dict(ts=r["ts"], actor=r["actor"], event=r["event"], payload=json.loads(r["payload"])) for r in c.execute("select * from ledger where couple_id=? order by id", (cid,))]
    return {"chain_valid": db.verify(c, cid), "events": rows}

import datetime
TAG = {"tag": [{"code": "synthetic-prototype", "display": "FHIR-style, not validated; contains no genetic results"}]}
ORDER = {"urgent": 0, "high": 1, "standard": 2}
class History(BaseModel): answers: dict[str, bool | str]
class Quiz(BaseModel): lang: str; score: int; total: int
def staff_only(tok):
    if tok not in (COUNSELOR, COORD): raise HTTPException(403, "staff only")
def case_info(c, cid):
    cp = c.execute("select * from couples where id=?", (cid,)).fetchone()
    try: v, rel, both = compute(c, cid)
    except HTTPException: return None
    hist = any(any(v == "yes" for v in json.loads(r["answers"]).values()) for r in c.execute("select answers from history where couple_id=?", (cid,)))
    req = c.execute("select 1 from ledger where couple_id=? and event='counseling_requested'", (cid,)).fetchone() is not None
    severe = any(E.GENES[g][0] for g in v["genes_shown"])
    pr = "urgent" if distress_for(c, cid, None) else "high" if severe else "standard" if (v["escalate"] or hist) else None
    if pr is None: return None
    return {"case": cid, "priority": pr, "stage": STAGES[min(db.stage(c, cid), 4)], "history_reported": hist, "counseling_requested": req}
@app.put("/couples/{cid}/history")
def put_history(cid: str, b: History, x_token: str = Header()):
    c = db.conn(); p = partner_only(c, cid, x_token)
    ans = {k: ("yes" if v is True else "no" if v is False else v) for k, v in b.answers.items()}
    if set(ans) - set(E.HISTORY) or any(v not in ("yes", "no", "unsure") for v in ans.values()): raise HTTPException(422, "invalid answers")
    c.execute("insert or replace into history values(?,?,?)", (cid, p, json.dumps(ans))); db.log(c, cid, p, "history_stored", {"items": sum(v == "yes" for v in ans.values())}); c.commit(); return {"ok": True}
@app.get("/couples/{cid}/me")
def me(cid: str, x_token: str = Header()):
    c = db.conn(); p = partner_only(c, cid, x_token)
    r = c.execute("select answers from history where couple_id=? and partner=?", (cid, p)).fetchone(); flagged = bool(r and any(v == "yes" for v in json.loads(r["answers"]).values()))
    req = c.execute("select 1 from ledger where couple_id=? and event='counseling_requested' and actor=?", (cid, p)).fetchone() is not None
    return {"partner": p, "own_review": flagged, "counseling_requested": req, "message": "A counselor will review the family history you shared." if flagged else None}
@app.post("/couples/{cid}/request-counseling")
def request_counseling(cid: str, x_token: str = Header()):
    c = db.conn(); p = partner_only(c, cid, x_token); db.log(c, cid, p, "counseling_requested"); c.commit(); return {"ok": True}
@app.get("/couples/{cid}/privacy")
def privacy(cid: str, x_token: str = Header()):
    c = db.conn(); p = partner_only(c, cid, x_token)
    ev = [dict(ts=r["ts"], event=r["event"], payload=json.loads(r["payload"])) for r in c.execute("select * from ledger where couple_id=? and actor=? order by id", (cid, p))]
    return {"partner": p, "consent_now": db.consent(c, cid, p), "events": ev}
@app.delete("/couples/{cid}/my-data")
def delete_data(cid: str, x_token: str = Header()):
    c = db.conn(); p = partner_only(c, cid, x_token)
    c.execute("delete from results where couple_id=? and partner=?", (cid, p)); c.execute("delete from history where couple_id=? and partner=?", (cid, p))
    db.log(c, cid, p, "consent", {"share": False}); db.log(c, cid, p, "data_deleted"); c.commit(); return {"deleted": True}
@app.get("/cases")
def cases(x_token: str = Header()):
    staff_only(x_token); c = db.conn()
    out = [i for i in (case_info(c, r["id"]) for r in c.execute("select id from couples")) if i]
    return {"cases": sorted(out, key=lambda i: ORDER[i["priority"]])}
@app.post("/quiz")
def post_quiz(b: Quiz):
    if b.lang not in ("en", "ar") or b.total <= 0 or not (0 <= b.score <= b.total <= 20): raise HTTPException(422, "invalid")
    c = db.conn(); c.execute("insert into quiz values(?,?,?)", (b.lang, b.score, b.total)); c.commit(); return {"ok": True}
@app.get("/metrics")
def metrics(x_token: str = Header()):
    staff_only(x_token); c = db.conn(); ids = [r["id"] for r in c.execute("select id from couples")]; mins = []
    for cid in ids:
        a = c.execute("select ts from ledger where couple_id=? and event='couple_created'", (cid,)).fetchone()
        b = c.execute("select min(ts) t from ledger where couple_id=? and event='referral_advance'", (cid,)).fetchone()
        if a and b["t"]: mins.append((b["t"] - a["ts"]) / 60)
    quiz = {r["lang"]: {"avg_pct": round(100 * r["s"] / r["t"], 1), "n": r["n"]} for r in c.execute("select lang, sum(score) s, sum(total) t, count(*) n from quiz group by lang")}
    return {"cases": len(ids), "needing_review": sum(1 for i in ids if case_info(c, i)), "mean_minutes_to_first_referral_step": round(sum(mins) / len(mins), 1) if mins else None, "quiz": quiz, "note": "Prototype demo data. Not real outcomes."}
@app.get("/couples/{cid}/fhir")
def fhir(cid: str, x_token: str = Header()):
    c = db.conn(); role = auth(c, cid, x_token)
    if role not in ("counselor", "coordinator"): raise HTTPException(403, "staff only")
    ents = []
    for p in "AB":
        pid = f"{cid}-{p}"; on = db.consent(c, cid, p)
        ents.append({"resourceType": "Patient", "id": pid, "meta": TAG})
        ents.append({"resourceType": "Consent", "id": "consent-" + pid, "status": "active" if on else "inactive", "scope": {"text": "Share gene-level match with partner"}, "patient": {"reference": "Patient/" + pid}, "provision": {"type": "permit" if on else "deny"}, "meta": TAG})
    try: esc = compute(c, cid)[0]["escalate"]
    except HTTPException: esc = False
    if esc:
        st = db.stage(c, cid)
        ents.append({"resourceType": "ServiceRequest", "id": "referral-" + cid, "status": "active", "intent": "order", "code": {"text": "Genetic counseling referral"}, "subject": {"reference": "Group/" + cid}, "meta": TAG})
        ents.append({"resourceType": "Task", "id": "task-" + cid, "status": "completed" if st >= 4 else "in-progress" if st else "requested", "intent": "order", "description": STAGES[min(st, 4)], "focus": {"reference": "ServiceRequest/referral-" + cid}, "meta": TAG})
    for r in c.execute("select * from ledger where couple_id=? order by id limit 50", (cid,)):
        ents.append({"resourceType": "AuditEvent", "id": f"audit-{r['id']}", "recorded": datetime.datetime.fromtimestamp(r["ts"], datetime.timezone.utc).isoformat(), "agent": [{"who": {"display": r["actor"]}}], "type": {"display": r["event"]}, "meta": TAG})
    return {"resourceType": "Bundle", "type": "collection", "meta": TAG, "entry": [{"resource": e} for e in ents]}
@app.post("/couples/{cid}/brief")
def brief(cid: str, b: Brief, x_token: str = Header()):
    c = db.conn(); p = partner_only(c, cid, x_token)
    if E.urgent(b.questions):
        db.log(c, cid, p, "urgent_wording_shown"); c.commit(); return {"urgent": True, "message": E.EMERGENCY["en"]}
    v, rel, both = compute(c, cid, viewer=p)
    q = "".join(ch for ch in b.questions[:1000] if ch.isprintable() or ch == "\n")
    summary = ("Shared carrier gene(s): " + ", ".join(v["genes_shown"]) if v["genes_shown"] else "No shared carrier finding on the agreed genes") if both else "Couple comparison not available (consent incomplete)"
    db.log(c, cid, p, "brief_generated"); c.commit()
    return {"reference": f"AMNA-{cid[:4].upper()}-{cid[4:8].upper()}", "generated": datetime.date.today().isoformat(), "shared_genes": v["genes_shown"], "summary": summary, "questions": q, "note": "Pseudonymous, not anonymous. Education and decision support, not clinical advice. Prepares you for a visit; it does not replace counseling."}
@app.middleware("http")
async def security_headers(request, call_next):
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"; resp.headers["Referrer-Policy"] = "no-referrer"
    if resp.headers.get("content-type", "").startswith("application/json"): resp.headers["Cache-Control"] = "no-store"
    return resp
@app.get("/health")
def health(): return {"ok": True}
from fastapi.staticfiles import StaticFiles
_FRONT = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.isdir(_FRONT): app.mount("/", StaticFiles(directory=_FRONT, html=True), name="ui")
