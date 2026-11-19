"""Python mirror of the app's deterministic engine and approved text (single source for tests)."""

GENES = {"HBB": (1, "Hemoglobin disorders (HBB)", "اضطرابات الهيموغلوبين (HBB)"),
         "GJB2": (0, "Inherited hearing loss (GJB2)", "فقدان السمع الوراثي (GJB2)"),
         "SMN1": (1, "Spinal muscular atrophy (SMN1)", "ضمور العضلات الشوكي (SMN1)"),
         "CFTR": (1, "Cystic fibrosis (CFTR)", "التليف الكيسي (CFTR)")}
EN = {"sh": lambda g: f"You both carry a change linked to {g}. Each pregnancy: 1 in 4 chance of an affected child. A chance, not a diagnosis.",
      "none": "No shared carrier finding. The panel is limited, so risk is lowered, not removed.",
      "rel": "Related partners may share changes this panel misses. A genetic counselor or doctor can help.",
      "vus": "One uncertain variant. Its meaning is unknown, so no risk figure is shown. Understanding can change over time. Ask a genetic counselor or doctor about re-checking it.",
      "lock": "Comparison locked until both partners consent.",
      "esc": "Review by a genetic counselor or doctor is recommended."}
AR = {"sh": lambda g: f"كلاكما يحمل تغيّرًا جينيًا مرتبطًا بـ{g}. في كل حمل احتمال واحد من أربعة لإصابة الطفل. هذا احتمال وليس تشخيصًا.",
      "none": "لا يوجد تغيّر جيني مشترك بينكما. وبما أن نطاق الفحص محدود، فالاحتمال أقل لكنه لا يزول.",
      "rel": "إذا كان بينكما قرابة، فقد تتشاركان تغيّرات جينية لا يغطيها هذا الفحص. يمكن للمستشار الوراثي أو الطبيب مساعدتكما.",
      "vus": "وُجد تغيّر جيني غير مؤكد الأثر. معناه غير معروف حتى الآن، لذا لا تُعرض نسبة خطر. قد يتغيّر الفهم العلمي مع الوقت، فيمكنك سؤال مستشار وراثي أو طبيب عن إعادة فحصه.",
      "lock": "المقارنة مقفلة حتى يوافق الشريكان.",
      "esc": "يُنصح بمراجعة مستشار وراثي أو طبيب مختص بالوراثة."}
LEVELS = {"Simple": "Think of two keys. A carrier has one working key and one that does not, and the door still opens. Trouble only happens if a child gets the non-working key from both parents.",
          "Standard": "A carrier has one changed copy of a gene and one working copy. Carriers usually have no symptoms. A child is affected only if both parents pass on a changed copy.",
          "Clinical": "Autosomal recessive inheritance. Two heterozygous carriers have a 25% recurrence risk per pregnancy, independent of earlier outcomes. Variants of uncertain significance (ACMG/AMP) are not used for risk counseling."}
FAM = {"en": "I had a genetic test. Some people carry gene changes and feel well. No one is to blame. If a gene change known to cause disease runs in your family, ask a genetics expert if a test may help."}

def risk(a, b):
    """Per-pregnancy outcome for one gene. a,b in {'0','1'}. Relatedness is NOT an input by design."""
    if "2" in (a, b): raise ValueError("VUS is never converted to a risk figure")
    if a == "1" and b == "1": return {"unaffected": .25, "carrier": .5, "affected": .25}
    if a == "1" or b == "1": return {"unaffected": .5, "carrier": .5, "affected": 0.0}
    return {"unaffected": 1.0, "carrier": 0.0, "affected": 0.0}

def couple_view(A, B, ca, cb, related=False, distress=False, lang="en", scope=None):
    T = EN if lang == "en" else AR; idx = 1 if lang == "en" else 2
    sc = set(GENES) if scope is None else set(scope); both = bool(ca and cb) and bool(sc); vus = any(A[g] == "2" or B[g] == "2" for g in GENES if g in sc)
    msgs, reasons, shown = [], [], []
    if not both:
        msgs.append(T["lock"])
    else:
        shared = [g for g in GENES if g in sc and A[g] == "1" and B[g] == "1"]
        for g in shared:
            msgs.append(T["sh"](GENES[g][idx])); shown.append(g)
            reasons.append(f"Both carriers: {g}" + (" (severe)" if GENES[g][0] else ""))
        if not shared: msgs.append(T["none"])
        if vus: msgs.append(T["vus"]); reasons.append("Uncertain variant")
        if related: msgs.append(T["rel"])
    if distress: reasons.append("Distress flagged")
    esc = bool(reasons)
    if esc: msgs.append(T["esc"])
    return {"text": " | ".join(msgs), "escalate": esc, "reasons": reasons, "genes_shown": shown}

def sbar(view, related, both):
    if not view["escalate"]: return "No handoff needed."
    sh = view["genes_shown"]; vus = any("Uncertain" in r for r in view["reasons"]); dist = any("Distress" in r for r in view["reasons"])
    a = ("Shared carrier gene(s): " + ", ".join(sh) + ". " if sh else "No shared carrier gene. ") + ("Uncertain variant present. " if vus else "") if both else "Couple comparison not available. "
    return ("S: Screening result needs counselor review.\nB: Synthetic panel (" + ", ".join(GENES) + f"). Related partners: {'yes' if related else 'no'}. Couple consent: {'both given' if both else 'incomplete'}.\n"
            f"A: {a}{'Distress flagged. ' if dist else ''}\nR: Genetic counseling visit; confirmatory testing as indicated.\nGenerated from fixed rules, not by a language model.")

HISTORY = {"sibling_condition": "A sibling or close relative has thalassemia, SMA, cystic fibrosis or another inherited condition",
           "infant_death": "A child or sibling died in infancy from an unknown cause",
           "hearing_or_blood": "Early hearing loss or a blood disorder runs in the family",
           "relatives_married": "Our families have several marriages between relatives",
           "current_pregnancy": "I or my partner is currently pregnant and have a genetic screening concern",
           "known_diagnosis": "I or my partner has a diagnosed inherited genetic condition"}

import re as _re
URGENT = _re.compile(r"suicid|kill myself|end(ing)? my (own )?life|want to die|hurt myself|self[- ]?harm|emergency|can'?t breathe|chest pain|bleeding heavily|انتحار|أقتل نفسي|أريد أن أموت|طوارئ|نزيف", _re.I)
EMERGENCY = {"en": "This tool cannot help in an emergency. If you or someone else is in danger or needs urgent medical help, call your local emergency number now or go to the nearest hospital. If you feel unsafe, contact someone you trust.",
             "ar": "لا تستطيع هذه الأداة المساعدة في حالات الطوارئ. إذا كنت أنت أو شخص آخر في خطر أو تحتاج إلى مساعدة طبية عاجلة، فاتصل برقم الطوارئ المحلي الآن أو توجه إلى أقرب مستشفى. وإذا كنت لا تشعر بالأمان، فتواصل مع شخص تثق به."}
def urgent(text): return bool(URGENT.search(text or ""))
