
import re, json, requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
def _clean_text(html: str) -> str:
    try:
        from readability import Document
        doc = Document(html)
        soup = BeautifulSoup(doc.summary(html_partial=True), "html.parser")
        return soup.get_text(separator=" ")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")
        for t in soup(["script","style","noscript"]): t.decompose()
        return soup.get_text(separator=" ")

def _has(words: List[str], text: str) -> bool:
    tl=text.lower()
    return any(w.lower() in tl for w in words)

def _num(pattern: str, text: str) -> Optional[float]:
    m=re.search(pattern, text, re.I)
    if not m: return None
    try: return float(m.group(1))
    except: return None

def _guess_timing(text: str) -> str:
    if re.search(r"\breal[-\s]?time\b", text, re.I): return "real-time"
    if re.search(r"\bnear[-\s]?real[-\s]?time\b", text, re.I): return "near-real-time"
    if re.search(r"\bbatch\b", text, re.I): return "batch"
    return "near-real-time"

def _guess_location(text: str) -> str:
    tl=text.lower()
    if _has(["in-ehr","within ehr","inside ehr","embedded in ehr","epic","cerner","in emr","within emr"], tl): return "in-EHR"
    if _has(["email","mail"], tl): return "email"
    if _has(["sms","text message"], tl): return "sms"
    return "external"

def ingest_from_url(url: str, assume: str="balanced") -> Dict[str, Any]:
    r=requests.get(url, timeout=20)
    r.raise_for_status()
    html=r.text
    tx=_clean_text(html)
    tl=tx.lower()
    name=urlparse(url).path.split("/")[-1] or urlparse(url).netloc
    timing=_guess_timing(tl)
    location=_guess_location(tl)
    ms=_num(r"(\d+(?:\.\d+)?)\s*ms", tl)
    sec=_num(r"(\d+(?:\.\d+)?)\s*sec(?:ond)?s?", tl)
    latency=int(ms) if ms is not None else int(float(sec)*1000) if sec is not None else None
    has_reco=_has(["recommendation","recommender","suggested order","care pathway","best practice"], tl)
    one_click=_has(["one-click","single click","1-click","order with one click"], tl)
    order_set=_has(["order set","orderset","order-set"], tl)
    auto_fetch=85.0 if _has(["auto-populate","prefill","auto-fill","fhir","hl7"], tl) else 40.0 if _has(["manual entry","data entry required"], tl) else None
    mfields=_num(r"(\d+)\s+(?:fields|form fields|inputs)", tl)
    clicks=_num(r"(\d+)\s+clicks?", tl)
    triggers=[]
    for trig,key in [("medication order","med_order"),("abnormal lab","abnormal_lab"),("vital","vitals_change"),("diagnosis","new_diagnosis"),("triage","triage")]:
        if trig in tl: triggers.append(key)
    proactive=_has(["proactive","auto-trigger","automatically triggers","push alert"], tl)
    tier="moderate" if _has(["tiered","severity levels","priority levels","low/medium/high","alert"], tl) else None
    silence=_has(["snooze","mute","silence","suppression rules","dampening"], tl)
    req_override=_has(["override reason","reason required"], tl)
    over=_num(r"(\d+(?:\.\d+)?)\s*%?\s*override", tl)
    has_kpis=_has(["kpi","key performance indicator","metric"], tl)
    dashboard=_has(["dashboard","analytics console"], tl)
    rd=_num(r"retrain(?:ing)?\s+every\s+(\d+)\s+days", tl) or _num(r"(\d+)\s+days\s+retrain", tl)
    retrain=int(rd) if rd is not None else None
    incident=_has(["incident","safety event","quality review","capa"], tl)
    def assume_val(maybe, good, mid, bad):
        if maybe is not None: return maybe
        return {"optimistic":good,"balanced":mid,"conservative":bad}[assume]
    spec={
        "name": name,
        "workflow": {"stages": ["order_entry"] if _has(["order","prescribe"], tl) else ["documentation"], "click_count_to_act": assume_val(int(clicks) if clicks is not None else None, 2, 3, 4)},
        "delivery": {"timing": timing, "location": location, "latency_ms": assume_val(latency, 250, 600, 1200)},
        "actionability": {"has_recommendation": has_reco, "one_click": one_click, "has_order_set": order_set},
        "data_entry": {"auto_fetch_pct": assume_val(auto_fetch, 85.0, 60.0, 30.0), "manual_fields": int(mfields) if mfields is not None else {"optimistic":1,"balanced":3,"conservative":5}[assume]},
        "defaults_safety": {"smart_defaults": _has(["default","preselected","pre-selected"], tl), "opt_out_when_safe": _has(["opt-out","default on"], tl), "safety_rails": _has(["hard stop","soft stop","guardrail","constraint"], tl)},
        "proactivity": {"triggers": sorted(list(set(triggers))), "proactive": proactive},
        "team_scope": {"roles_supported": []},
        "transparency": {"shows_rationale": _has(["rationale","why","explain"], tl), "links_to_evidence": _has(["evidence","guideline","reference","citation"], tl), "explainability": _has(["explainability","interpretable","shap","saliency"], tl)},
        "fatigue": {"tiering": tier, "silence_rules": silence, "require_override_reason": req_override, "observed_override_rate_pct": round(float(over),1) if over is not None else None},
        "monitoring": {"has_kpis": has_kpis, "dashboard": dashboard, "retrain_days": retrain if retrain is not None else {"optimistic":120,"balanced":180,"conservative":365}[assume], "incident_process": incident},
        "governance": {"owner": None, "versioning": _has(["version","semver","release notes"], tl), "change_control": _has(["change control","cab","governance"], tl), "privacy_security_ok": _has(["hipaa","iso 27001","soc 2","pdp","gdpr"], tl)},
        "extra": {"source_url": url, "assumption_mode": assume}
    }
    return spec
