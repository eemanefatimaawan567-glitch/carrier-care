import os, tempfile, sqlite3
os.environ["CARRIER_DB"] = tempfile.mktemp(suffix=".db")
from fastapi.testclient import TestClient
from app.main import app
from app import db
cl = TestClient(app); G = ["HBB", "GJB2", "SMN1", "CFTR"]; CO = {"X-Token": "counselor-demo"}; CD = {"X-Token": "coordinator-demo"}
def mk(rel=False):
    r = cl.post("/couples", json={"related": rel}).json(); return r["couple_id"], {"X-Token": r["token_a"]}, {"X-Token": r["token_b"]}
def res(cid, h, **kw):
    d = {g: "0" for g in G}; d.update(kw); assert cl.put(f"/couples/{cid}/results", json={"results": d}, headers=h).status_code == 200
def cons(cid, h, v): assert cl.put(f"/couples/{cid}/consent", json={"share": v}, headers=h).status_code == 200
def view(cid, h): return cl.get(f"/couples/{cid}/view", headers=h).json()
def test_consent_gating_and_revocation():
    cid, a, b = mk(); res(cid, a, HBB="1"); res(cid, b, HBB="1")
    assert "locked" in view(cid, a)["text"] and "HBB" not in view(cid, b)["text"]
    cons(cid, a, True); assert "locked" in view(cid, b)["text"]
    cons(cid, b, True); assert view(cid, a)["genes_shown"] == ["HBB"]
    cons(cid, a, False); v = view(cid, b); assert "locked" in v["text"] and v["genes_shown"] == []
def test_unilateral_carrier_never_revealed():
    cid, a, b = mk(); res(cid, a, CFTR="1"); res(cid, b); cons(cid, a, True); cons(cid, b, True)
    for h in (a, b): v = view(cid, h); assert "CFTR" not in v["text"] and not v["escalate"]
def test_roles_and_isolation():
    cid, a, b = mk(); cid2, a2, _ = mk(); res(cid, a); res(cid, b)
    assert cl.get(f"/couples/{cid}/handoff", headers=a).status_code == 403
    assert cl.get(f"/couples/{cid}/view", headers=a2).status_code == 403
    assert cl.get(f"/couples/{cid}/audit", headers=a).status_code == 403
    assert cl.post(f"/couples/{cid}/referral/advance", headers=CO).status_code == 403
def test_referral_flow_and_handoff():
    cid, a, b = mk(True); res(cid, a, HBB="1"); res(cid, b, HBB="1"); cons(cid, a, True); cons(cid, b, True)
    assert view(cid, a)["escalate"] and "HBB" in cl.get(f"/couples/{cid}/handoff", headers=CO).json()["sbar"]
    for _ in range(4): assert cl.post(f"/couples/{cid}/referral/advance", headers=CD).status_code == 200
    assert cl.post(f"/couples/{cid}/referral/advance", headers=CD).status_code == 409
def test_ledger_has_no_results_and_detects_tampering():
    cid, a, b = mk(); res(cid, a, CFTR="1"); res(cid, b); cons(cid, a, True)
    out = cl.get(f"/couples/{cid}/audit", headers=CO).json(); assert out["chain_valid"] and "CFTR" not in str(out["events"])
    c = sqlite3.connect(db.path()); c.execute("update ledger set payload='{\"share\": false}' where couple_id=? and event='consent'", (cid,)); c.commit()
    assert cl.get(f"/couples/{cid}/audit", headers=CO).json()["chain_valid"] is False
def test_health_and_ui_served():
    assert cl.get("/health").json() == {"ok": True}
    r = cl.get("/"); assert r.status_code == 200 and "Amanah" in r.text
def test_view_returns_reasons_without_leaking():
    cid, a, b = mk(); res(cid, a, CFTR="1", GJB2="2"); res(cid, b); cons(cid, a, True)
    v = view(cid, b); assert v["reasons"] == [] and "CFTR" not in str(v) and "GJB2" not in str(v)
def hist(cid, h, **kw): assert cl.put(f"/couples/{cid}/history", json={"answers": kw}, headers=h).status_code == 200
def mine(cid, x): return [i for i in cl.get("/cases", headers=CO).json()["cases"] if i["case"] == cid]
def test_family_history_is_private_and_reaches_counselor():
    cid, a, b = mk(); res(cid, a); res(cid, b); cons(cid, a, True); cons(cid, b, True); hist(cid, a, sibling_condition=True)
    assert view(cid, a) == view(cid, b)
    assert cl.get(f"/couples/{cid}/me", headers=a).json()["own_review"] is True and cl.get(f"/couples/{cid}/me", headers=b).json()["own_review"] is False
    assert mine(cid, 0)[0]["history_reported"] and "Family history" in cl.get(f"/couples/{cid}/handoff", headers=CO).json()["sbar"]
    assert cl.get("/cases", headers=a).status_code == 403
def test_queue_priority_and_visit_request():
    cid, a, b = mk(); res(cid, a, HBB="1"); res(cid, b, HBB="1"); cons(cid, a, True); cons(cid, b, True)
    assert mine(cid, 0)[0]["priority"] == "high"
    assert cl.post(f"/couples/{cid}/request-counseling", headers=a).status_code == 200 and mine(cid, 0)[0]["counseling_requested"]
    cl.put(f"/couples/{cid}/flags", json={"distress": True}, headers=a); assert mine(cid, 0)[0]["priority"] == "urgent"
def test_privacy_dashboard_and_deletion():
    cid, a, b = mk(); res(cid, a, CFTR="1"); res(cid, b); cons(cid, a, True); cons(cid, b, True)
    p = cl.get(f"/couples/{cid}/privacy", headers=a).json(); assert p["consent_now"] and all(e["event"] != "x" for e in p["events"]) and "CFTR" not in str(p)
    assert cl.delete(f"/couples/{cid}/my-data", headers=a).json()["deleted"]
    assert cl.get(f"/couples/{cid}/privacy", headers=a).json()["consent_now"] is False and cl.get(f"/couples/{cid}/view", headers=b).status_code == 409
def test_fhir_has_no_results_and_is_staff_only():
    cid, a, b = mk(); res(cid, a, CFTR="1"); res(cid, b); cons(cid, a, True); cons(cid, b, True)
    r = cl.get(f"/couples/{cid}/fhir", headers=CO); assert r.status_code == 200 and "CFTR" not in r.text and "Consent" in r.text
    assert cl.get(f"/couples/{cid}/fhir", headers=a).status_code == 403
def test_quiz_and_metrics():
    assert cl.post("/quiz", json={"lang": "en", "score": 3, "total": 4}).status_code == 200
    assert cl.post("/quiz", json={"lang": "xx", "score": 3, "total": 4}).status_code == 422
    m = cl.get("/metrics", headers=CO).json(); assert m["quiz"]["en"]["n"] >= 1 and m["cases"] >= 1
    assert cl.get("/metrics").status_code == 422 or cl.get("/metrics").status_code == 403
def consg(cid, h, genes): return cl.put(f"/couples/{cid}/consent", json={"share": True, "genes": genes}, headers=h)
def test_granular_consent_scope():
    cid, a, b = mk(); res(cid, a, HBB="1", GJB2="1"); res(cid, b, HBB="1", GJB2="1")
    assert consg(cid, a, ["HBB"]).status_code == 200 and consg(cid, b, ["HBB", "GJB2"]).status_code == 200
    v = view(cid, a); assert v["genes_shown"] == ["HBB"] and "GJB2" not in str(v)
    cid2, a2, b2 = mk(); res(cid2, a2, GJB2="2"); res(cid2, b2); consg(cid2, a2, ["HBB"]); consg(cid2, b2, ["HBB", "GJB2"])
    v2 = view(cid2, b2); assert not v2["escalate"] and "uncertain" not in v2["text"]
    assert consg(cid, a, []).status_code == 422 and consg(cid, a, ["XXX"]).status_code == 422
    consg(cid, b, ["GJB2"]); assert "locked" in view(cid, a)["text"]
def test_intake_brief_is_pseudonymous_and_scoped():
    cid, a, b = mk(); res(cid, a, HBB="1", CFTR="1"); res(cid, b, HBB="1", CFTR="1"); consg(cid, a, ["HBB"]); consg(cid, b, ["HBB"])
    r = cl.post(f"/couples/{cid}/brief", json={"questions": "What are our options?"}, headers=a).json()
    assert r["reference"].startswith("AMNA-") and r["shared_genes"] == ["HBB"] and "CFTR" not in str(r) and r["questions"] == "What are our options?"
    assert cl.post(f"/couples/{cid}/brief", json={}, headers=CO).status_code == 403
    cid2, a2, b2 = mk(); res(cid2, a2, HBB="1"); res(cid2, b2, HBB="1"); cons(cid2, a2, True)
    r2 = cl.post(f"/couples/{cid2}/brief", json={}, headers=a2).json(); assert r2["shared_genes"] == [] and "not available" in r2["summary"]
    assert any(e["event"] == "brief_generated" for e in cl.get(f"/couples/{cid}/audit", headers=CO).json()["events"])
def test_family_history_not_sure_option():
    cid, a, b = mk(); res(cid, a); res(cid, b); cons(cid, a, True); cons(cid, b, True)
    hist(cid, a, infant_death="unsure")
    assert not mine(cid, 0) and cl.get(f"/couples/{cid}/me", headers=a).json()["own_review"] is False
    hist(cid, a, infant_death="unsure", sibling_condition="yes")
    assert mine(cid, 0)[0]["history_reported"]
    s = cl.get(f"/couples/{cid}/handoff", headers=CO).json()["sbar"]; assert "not sure about" in s and "Family history (self-reported)" in s
    assert cl.put(f"/couples/{cid}/history", json={"answers": {"infant_death": "maybe"}}, headers=a).status_code == 422
def test_distress_is_private_to_the_partner_who_flags():
    cid, a, b = mk(); res(cid, a); res(cid, b); cons(cid, a, True); cons(cid, b, True)
    assert cl.put(f"/couples/{cid}/flags", json={"distress": True}, headers=a).status_code == 200
    vb = view(cid, b); assert not vb["escalate"] and vb["reasons"] == [] and "distress" not in str(vb).lower()
    va = view(cid, a); assert va["escalate"] and "Distress flagged" in va["reasons"]
    assert mine(cid, 0)[0]["priority"] == "urgent"
def test_partner_tokens_hashed_at_rest_and_headers():
    r = cl.post("/couples", json={}).json(); c = sqlite3.connect(db.path())
    rows = [x[0] for x in c.execute("select token from tokens")]
    assert r["token_a"] not in rows and all(len(x) == 64 for x in rows)
    h = cl.get("/health").headers; assert h["x-content-type-options"] == "nosniff" and h["referrer-policy"] == "no-referrer"
    assert cl.get("/cases", headers={"X-Token": "wrong"}).status_code == 403
def test_emergency_wording_stops_the_brief():
    cid, a, b = mk(); res(cid, a); res(cid, b); cons(cid, a, True); cons(cid, b, True)
    r = cl.post(f"/couples/{cid}/brief", json={"questions": "I want to die"}, headers=a).json()
    assert r["urgent"] is True and "emergency" in r["message"].lower() and "reference" not in r
    ok = cl.post(f"/couples/{cid}/brief", json={"questions": "How long does counseling take?"}, headers=a).json()
    assert "reference" in ok and not ok.get("urgent")

def test_new_referral_prompts_prioritize_without_partner_disclosure():
    for key in ("current_pregnancy", "known_diagnosis"):
        cid, a, b = mk()
        res(cid, a); res(cid, b)
        cons(cid, a, False); cons(cid, b, False)
        response = cl.put(f"/couples/{cid}/history", json={"answers": {key: "yes"}}, headers=a)
        assert response.status_code == 200
        queue = cl.get("/cases", headers=CO)
        assert queue.status_code == 200
        case = next(x for x in queue.json()["cases"] if x["case"] == cid)
        assert case["priority"] == "high"
        assert "locked" in view(cid, b)["text"]
        assert cl.get(f"/couples/{cid}/me", headers=b).json()["own_review"] is False
