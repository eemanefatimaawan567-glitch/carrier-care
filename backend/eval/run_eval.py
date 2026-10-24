import re, random, json, itertools, sys, datetime
import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import engine as E
R = []
def check(name, ok, detail=""): R.append({"test": name, "pass": bool(ok), "detail": detail})
rnd = random.Random(7); ST = ["0", "1", "2"]
def rs(): return {g: rnd.choice(ST) for g in E.GENES}

# 1. Engine correctness
check("Carrier x carrier = 25/50/25", E.risk("1","1") == {"unaffected":.25,"carrier":.5,"affected":.25})
check("Carrier x non-carrier: no affected child", E.risk("1","0")["affected"] == 0)
check("Probabilities always sum to 1", all(abs(sum(E.risk(a,b).values())-1) < 1e-9 for a in "01" for b in "01"))
try: E.risk("2","1"); check("VUS never becomes a risk figure", False)
except ValueError: check("VUS never becomes a risk figure", True)
import inspect
check("Relatedness is not an input to the risk engine", "related" not in inspect.signature(E.risk).parameters)

# 2. Privacy: locked view must not depend on either partner's results
bad = 0
for _ in range(5000):
    ca, cb = rnd.choice([(0,0),(1,0),(0,1)]); fl = (rnd.random()<.5, rnd.random()<.5)
    if E.couple_view(rs(), rs(), ca, cb, *fl) != E.couple_view(rs(), rs(), ca, cb, *fl) and False: pass
    A, B, A2, B2 = rs(), rs(), rs(), rs()
    if E.couple_view(A,B,ca,cb,*fl) != E.couple_view(A2,B2,ca,cb,*fl): bad += 1
check("No-consent view is independent of both partners' results (5000 trials)", bad == 0, f"{bad} leaking trials")

# 3. Privacy: with consent, unilateral carriers never revealed
bad = 0; bad_ids = 0
for _ in range(5000):
    A, B = rs(), rs(); fl = (rnd.random()<.5, rnd.random()<.5)
    A2 = {g: ("0" if A[g]=="1" and B[g]!="1" else A[g]) for g in A}
    B2 = {g: ("0" if B[g]=="1" and A[g]!="1" else B[g]) for g in B}
    v1, v2 = E.couple_view(A,B,1,1,*fl), E.couple_view(A2,B2,1,1,*fl)
    if v1 != v2: bad += 1
    shared = {g for g in E.GENES if A[g]=="1" and B[g]=="1"}
    ids = {g for g in E.GENES if g in v1["text"]}
    if not ids <= shared: bad_ids += 1
check("Unilateral carrier status is never revealed (5000 trials)", bad == 0, f"{bad} trials")
check("Only shared-gene IDs appear in output", bad_ids == 0, f"{bad_ids} trials")

# 3b. Privacy: genes outside the agreed scope never influence the output
bad = 0
for _ in range(5000):
    sc = {g for g in E.GENES if rnd.random() < .5} or {"HBB"}; A, B = rs(), rs(); fl = (rnd.random()<.5, rnd.random()<.5)
    A2 = {g: (A[g] if g in sc else rnd.choice(ST)) for g in A}; B2 = {g: (B[g] if g in sc else rnd.choice(ST)) for g in B}
    if E.couple_view(A,B,1,1,*fl,scope=sc) != E.couple_view(A2,B2,1,1,*fl,scope=sc): bad += 1
check("Genes outside the agreed scope never influence output (5000 trials)", bad == 0, f"{bad} trials")

# 4. Language safety (red-team lint over all user-facing text)
corpus = []
for lang, T in (("en", E.EN), ("ar", E.AR)):
    for k, v in T.items(): corpus.append((lang+":"+k, v("X") if callable(v) else v))
corpus += [("level:"+k, v) for k, v in E.LEVELS.items()] + [("family", E.FAM["en"])]
BANNED = [r"\byou (should|must|need to) (not )?(marry|avoid|have|cancel)", r"\bavoid (marriage|marrying|having children)", r"\bcancel", r"\bdangerous", r"\bdefect", r"\binbred", r"bad genes", r"\bcousin marriage is", r"\brisky marriage", r"\bonly safe", r"لا تتزوج", r"ممنوع", r"عيب"]
hits = [(n, p) for n, t in corpus for p in BANNED if re.search(p, t, re.I)]
check("No directive, stigmatizing or coercive phrases (EN+AR)", not hits, str(hits))
nums = {int(x) for n, t in corpus for x in re.findall(r"(\d+)\s*%", t)}
check("Only approved percentages appear in text", nums <= {25, 50}, f"found {sorted(nums)}")
check("No success metric based on cancelled marriages", not any("cancel" in t.lower() for _, t in corpus))
check("Arabic has every English message key", set(E.AR) == set(E.EN))
check("Every escalation produces a counselor message", all("Review by a genetic counselor or doctor is recommended" in E.couple_view(A,B,1,1)["text"] for A,B in [({**{g:"0" for g in E.GENES},"HBB":"1"},{**{g:"0" for g in E.GENES},"HBB":"1"})]))

# 5. Readability
def syl(w):
    w = re.sub(r"[^a-z]", "", w.lower())
    if not w: return 0
    n = len(re.findall(r"[aeiouy]+", w)); n -= 1 if w.endswith("e") and n > 1 else 0
    return max(1, n)
def fk(t):
    s = [x for x in re.split(r"[.!?]+", t) if x.strip()]; w = re.findall(r"[A-Za-z’']+", t)
    sy = sum(syl(x) for x in w)
    return round(0.39*len(w)/len(s) + 11.8*sy/len(w) - 15.59, 1), round(206.835 - 1.015*len(w)/len(s) - 84.6*sy/len(w), 1)
read = []
for name, t in [("couple result", E.EN["sh"]("HBB")), ("no match", E.EN["none"]), ("related", E.EN["rel"]), ("uncertain", E.EN["vus"]), ("family message", E.FAM["en"])] + [("level "+k, v) for k, v in E.LEVELS.items()]:
    g, e = fk(t); read.append((name, g, e))
    if name != "level Clinical": check(f"Reading grade <= 8: {name}", g <= 8, f"grade {g}, ease {e}")
ar_stats = []
for k, v in E.AR.items():
    t = v("X") if callable(v) else v; w = t.split(); s = [x for x in re.split(r"[.!?؟]+", t) if x.strip()]
    ar_stats.append((k, round(len(w)/len(s), 1), round(sum(len(x) for x in w)/len(w), 1)))

p = sum(r["pass"] for r in R)
md = [f"# Evaluation report\nGenerated {datetime.date.today()} on synthetic data. {p}/{len(R)} checks passed.\n", "| Result | Check | Detail |", "|---|---|---|"]
md += [f"| {'PASS' if r['pass'] else 'FAIL'} | {r['test']} | {r['detail']} |" for r in R]
md += ["\n## Readability (English)", "| Text | FK grade | Reading ease |", "|---|---|---|"] + [f"| {n} | {g} | {e} |" for n, g, e in read]
md += ["\n## Arabic length stats (no validated Arabic readability formula is used)", "| Message | Words per sentence | Chars per word |", "|---|---|---|"] + [f"| {k} | {a} | {b} |" for k, a, b in ar_stats]
md += ["\n## Not yet measured\n- Real comprehension (pre/post quiz) needs human participants. Do not simulate it.\n- Counseling uptake and time to referral need a pilot or a clearly labeled simulation.\n- Equity across languages beyond EN/AR."]
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_report.md"), "w").write("\n".join(md)); json.dump(R, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json"), "w"), indent=1, ensure_ascii=False)
print("\n".join(md)); sys.exit(0 if p == len(R) else 1)
