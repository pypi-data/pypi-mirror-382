
from typing import Dict, Any, List, Tuple
from .schema import CDSInput
from .commandments import COMMANDMENTS, TITLE_BY_KEY, DEFINITION_BY_KEY

def _cap01(x: float) -> float:
    return max(0.0, min(1.0, x))

def _score_speed(m: CDSInput):
    s=0.0; notes=[]
    if m.delivery.latency_ms is not None and m.delivery.latency_ms <= 300: s+=0.7
    elif m.delivery.latency_ms is not None and m.delivery.latency_ms <= 1000: s+=0.4; notes.append("Reduce backend latency toward ≤300 ms")
    else: notes.append("Specify and optimize latency")
    if m.workflow.click_count_to_act is not None and m.workflow.click_count_to_act <= 2: s+=0.3
    else: notes.append("Ensure ≤2 clicks to act")
    return _cap01(s), notes

def _score_anticipate_realtime(m: CDSInput):
    s=0.0; notes=[]
    if m.delivery.timing in ["real-time","near-real-time"]: s+=0.5
    else: notes.append("Switch timing to real/near-real-time")
    triggers=set(t.lower() for t in m.proactivity.triggers)
    good={"med_order","abnormal_lab","vitals_change","new_diagnosis","triage"}
    s += 0.5*(len(triggers & good)/max(1,len(good)))
    if not triggers: notes.append("Add event-based triggers")
    return _cap01(s), notes

def _score_fit_workflow(m: CDSInput):
    s=0.0; notes=[]
    if any(stage in m.workflow.stages for stage in ["order_entry","triage","discharge","documentation","result_review"]): s+=0.5
    else: notes.append("Place CDS inline at decision steps")
    if m.delivery.location=="in-EHR": s+=0.5
    else: notes.append("Embed inside EHR")
    return _cap01(s), notes

def _score_micro_ux(m: CDSInput):
    s=0.0; notes=[]
    if m.defaults_safety.smart_defaults: s+=0.4
    if m.data_entry.auto_fetch_pct is not None and m.data_entry.auto_fetch_pct>=80: s+=0.3
    else: notes.append("Pre-fill ≥80% fields")
    if m.workflow.click_count_to_act is not None and m.workflow.click_count_to_act<=2: s+=0.3
    else: notes.append("Streamline to ≤2 clicks")
    return _cap01(s), notes

def _score_resist_stopping(m: CDSInput):
    s=0.0; notes=[]
    if m.defaults_safety.safety_rails: s+=0.4
    if m.fatigue.require_override_reason: s+=0.3
    if m.fatigue.tiering in ["low","moderate"]: s+=0.3
    else: notes.append("Tier alerts; hard stops only for high hazard")
    return _cap01(s), notes

def _score_redirect_not_block(m: CDSInput):
    s=0.0; notes=[]
    if m.actionability.has_recommendation: s+=0.4
    if m.actionability.one_click: s+=0.3
    if m.actionability.has_order_set: s+=0.3
    else: notes.append("Provide curated order sets and one-click corrections")
    return _cap01(s), notes

def _score_simplicity(m: CDSInput):
    s=0.0; notes=[]
    if m.actionability.has_recommendation and (m.data_entry.manual_fields is None or m.data_entry.manual_fields<=2): s+=0.6
    else: notes.append("Keep guidance concise and limit inputs")
    if m.transparency.shows_rationale: s+=0.2
    if m.transparency.links_to_evidence: s+=0.2
    return _cap01(s), notes

def _score_ask_only_when_needed(m: CDSInput):
    s=0.0; notes=[]
    if m.data_entry.auto_fetch_pct is not None:
        s+=0.8*_cap01(m.data_entry.auto_fetch_pct/100.0)
        if m.data_entry.auto_fetch_pct<80: notes.append("Increase auto-population toward ≥80%")
    else:
        notes.append("Declare auto-population coverage")
    if m.data_entry.manual_fields is not None and m.data_entry.manual_fields<=2: s+=0.2
    return _cap01(s), notes

def _score_monitor_feedback(m: CDSInput):
    s=0.0; notes=[]
    if m.monitoring.has_kpis: s+=0.3
    else: notes.append("Define KPIs including acceptance and overrides")
    if m.monitoring.dashboard: s+=0.3
    if m.monitoring.retrain_days is not None and m.monitoring.retrain_days<=180: s+=0.2
    else: notes.append("Set review or retraining ≤180 days")
    if m.monitoring.incident_process: s+=0.2
    return _cap01(s), notes

def _score_manage_knowledge(m: CDSInput):
    s=0.0; notes=[]
    if m.governance.versioning: s+=0.3
    else: notes.append("Version all artifacts")
    if m.governance.change_control: s+=0.3
    else: notes.append("Adopt change control with approvals")
    if m.governance.privacy_security_ok: s+=0.2
    else: notes.append("Document privacy and security posture")
    if m.governance.owner: s+=0.2
    else: notes.append("Assign explicit owner")
    return _cap01(s), notes

SCORERS = [
    ("speed", _score_speed),
    ("anticipate_realtime", _score_anticipate_realtime),
    ("fit_workflow", _score_fit_workflow),
    ("micro_ux", _score_micro_ux),
    ("resist_stopping", _score_resist_stopping),
    ("redirect_not_block", _score_redirect_not_block),
    ("simplicity", _score_simplicity),
    ("ask_only_when_needed", _score_ask_only_when_needed),
    ("monitor_feedback", _score_monitor_feedback),
    ("manage_knowledge", _score_manage_knowledge)
]

def evaluate(spec: Dict[str, Any]) -> Dict[str, Any]:
    m = CDSInput(**spec)
    scores={}
    notes={}
    total_w=0.0
    agg=0.0
    for key,fn in SCORERS:
        s,n = fn(m)
        scores[key]=round(100*s,1)
        notes[key]=n
    for c in COMMANDMENTS:
        total_w += c["weight"]
        agg += c["weight"]*(scores[c["key"]]/100.0)
    total=round(100*(agg/total_w),1)
    gaps=[]
    for c in COMMANDMENTS:
        k=c["key"]
        if scores[k] < 80.0:
            gaps.append({"commandment":c["title"],"definition":c["definition"],"score":scores[k],"why":c["hint"],"fix":notes.get(k,[])})
    return {"name": m.name,"scores":scores,"total":total,"gaps":gaps,"notes":notes,"titles":TITLE_BY_KEY,"definitions":DEFINITION_BY_KEY}
