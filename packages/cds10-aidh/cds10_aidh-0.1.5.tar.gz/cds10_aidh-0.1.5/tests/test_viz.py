
from cds10_aidh import evaluate, plot_scores
import matplotlib
matplotlib.use("Agg")

def test_plot_png(tmp_path):
    spec = {
        "name":"Spec",
        "workflow":{"stages":["order_entry"],"click_count_to_act":2},
        "delivery":{"timing":"real-time","location":"in-EHR","latency_ms":280},
        "actionability":{"has_recommendation":True,"one_click":True,"has_order_set":True},
        "data_entry":{"auto_fetch_pct":85,"manual_fields":1},
        "defaults_safety":{"smart_defaults":True,"opt_out_when_safe":True,"safety_rails":True},
        "proactivity":{"triggers":["med_order"],"proactive":True},
        "team_scope":{"roles_supported":["physician","nurse"]},
        "transparency":{"shows_rationale":True,"links_to_evidence":True,"explainability":False},
        "fatigue":{"tiering":"moderate","silence_rules":True,"require_override_reason":True,"observed_override_rate_pct":10},
        "monitoring":{"has_kpis":True,"dashboard":True,"retrain_days":120,"incident_process":True},
        "governance":{"owner":"CDS","versioning":True,"change_control":True,"privacy_security_ok":True}
    }
    res = evaluate(spec)
    out = tmp_path / "plot.png"
    plot_scores(res, out_png=str(out))
    assert out.exists() and out.stat().st_size > 0
