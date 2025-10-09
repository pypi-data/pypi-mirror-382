
from cds10_aidh import evaluate

def make_spec(latency=280, clicks=2, auto=85, manual_fields=1):
    return {
        "name":"Spec",
        "workflow":{"stages":["order_entry","documentation"],"click_count_to_act":clicks},
        "delivery":{"timing":"real-time","location":"in-EHR","latency_ms":latency},
        "actionability":{"has_recommendation":True,"one_click":True,"has_order_set":True},
        "data_entry":{"auto_fetch_pct":auto,"manual_fields":manual_fields},
        "defaults_safety":{"smart_defaults":True,"opt_out_when_safe":True,"safety_rails":True},
        "proactivity":{"triggers":["med_order","abnormal_lab"],"proactive":True},
        "team_scope":{"roles_supported":["physician","nurse","pharmacist"]},
        "transparency":{"shows_rationale":True,"links_to_evidence":True,"explainability":False},
        "fatigue":{"tiering":"moderate","silence_rules":True,"require_override_reason":True,"observed_override_rate_pct":15},
        "monitoring":{"has_kpis":True,"dashboard":True,"retrain_days":120,"incident_process":True},
        "governance":{"owner":"Owner","versioning":True,"change_control":True,"privacy_security_ok":True}
    }

def test_total_within_bounds():
    res = evaluate(make_spec())
    assert 0.0 <= res["total"] <= 100.0
    assert "speed" in res["scores"]

def test_latency_impacts_speed():
    fast = evaluate(make_spec(latency=280))
    slow = evaluate(make_spec(latency=2000))
    assert slow["scores"]["speed"] < fast["scores"]["speed"]
