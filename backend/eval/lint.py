import re
BANNED = [r"\byou (should|must|need to) (not )?(marry|avoid|have|cancel)", r"\bavoid (marriage|marrying|having children)", r"\bcancel", r"\bdangerous", r"\bdefect", r"\binbred", r"bad genes", r"\bcousin marriage is", r"\brisky marriage", r"\bonly safe", r"لا تتزوج", r"ممنوع", r"عيب"]
BANNED += [r"\b(you|we)\b.{0,25}\b(must|should|ought to|need to|have to)\b.{0,12}\bnot\b", r"\badvise (you )?(against|not)\b", r"\bnot (recommended|advisable) to (marry|have|proceed)\b", r"\bbad idea\b",
 r"\b(end(ing)?|break(ing)? off|call(ing)? off|cancel(l?ing)?|stop(ping)?)\b.{0,20}\b(engagement|marriage|wedding|relationship|union)\b", r"\bwill (be|become|get|suffer|have)\b.{0,15}\b(sick|ill|disabled|disease|suffer)\b", r"\bwill suffer\b",
 r"\binbreeding\b", r"\birresponsible\b", r"\bselfish\b", r"\bdanger(ous)?\b", r"\b(unsuitable|not suitable)\b", r"\bburden\b", r"\bdoomed\b", r"\bshould not (reproduce|have children|marry)\b", r"\bnot (safe|fit)\b", r"\bputting\b.{0,30}\bat risk\b"]
def flag(t):
    return [p for p in BANNED if re.search(p, t, re.I)]
