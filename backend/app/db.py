import sqlite3, json, hashlib, time, os
def path(): return os.environ.get("CARRIER_DB", "carrier.db")
def conn():
    c = sqlite3.connect(path()); c.row_factory = sqlite3.Row; return c
def init():
    c = conn(); c.executescript("""
create table if not exists couples(id text primary key, related int, distress int default 0);
create table if not exists tokens(token text primary key, couple_id text, role text);
create table if not exists results(couple_id text, partner text, genes text, primary key(couple_id, partner));
create table if not exists flags(couple_id text, partner text, distress int, primary key(couple_id, partner));
create table if not exists history(couple_id text, partner text, answers text, primary key(couple_id, partner));
create table if not exists quiz(lang text, score int, total int);
create table if not exists ledger(id integer primary key autoincrement, couple_id text, ts real, actor text, event text, payload text, prev text, hash text);"""); c.commit(); c.close()
def _h(prev, ts, actor, event, p): return hashlib.sha256((prev + repr(ts) + actor + event + p).encode()).hexdigest()
def log(c, cid, actor, event, payload=None):
    """Append-only, hash-chained ledger. Payloads never contain genetic results."""
    row = c.execute("select hash from ledger where couple_id=? order by id desc limit 1", (cid,)).fetchone()
    prev = row["hash"] if row else "0" * 64; ts = time.time(); p = json.dumps(payload or {}, sort_keys=True)
    c.execute("insert into ledger(couple_id,ts,actor,event,payload,prev,hash) values(?,?,?,?,?,?,?)", (cid, ts, actor, event, p, prev, _h(prev, ts, actor, event, p)))
def verify(c, cid):
    prev = "0" * 64
    for r in c.execute("select * from ledger where couple_id=? order by id", (cid,)):
        if r["prev"] != prev or _h(prev, r["ts"], r["actor"], r["event"], r["payload"]) != r["hash"]: return False
        prev = r["hash"]
    return True
def consent(c, cid, partner):
    r = c.execute("select payload from ledger where couple_id=? and event='consent' and actor=? order by id desc limit 1", (cid, partner)).fetchone()
    return bool(r and json.loads(r["payload"]).get("share"))
def stage(c, cid): return c.execute("select count(*) n from ledger where couple_id=? and event='referral_advance'", (cid,)).fetchone()["n"]

def consent_genes(c, cid, partner):
    """Genes this partner currently allows in the couple match (empty set = no consent)."""
    from .engine import GENES
    r = c.execute("select payload from ledger where couple_id=? and event='consent' and actor=? order by id desc limit 1", (cid, partner)).fetchone()
    if not r: return set()
    p = json.loads(r["payload"])
    if not p.get("share"): return set()
    return set(p["genes"]) if p.get("genes") else set(GENES)
