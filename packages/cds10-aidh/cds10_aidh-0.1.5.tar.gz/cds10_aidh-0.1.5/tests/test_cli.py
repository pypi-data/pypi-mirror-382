
import sys, subprocess, yaml
from pathlib import Path

def test_cli_runs(tmp_path):
    spec = {
        "name":"CLI",
        "workflow":{"stages":["order_entry"],"click_count_to_act":2},
        "delivery":{"timing":"real-time","location":"in-EHR","latency_ms":300},
        "actionability":{"has_recommendation":True,"one_click":True,"has_order_set":True},
        "data_entry":{"auto_fetch_pct":80,"manual_fields":2},
        "defaults_safety":{"smart_defaults":True,"opt_out_when_safe":True,"safety_rails":True},
        "proactivity":{"triggers":["med_order"],"proactive":True},
        "team_scope":{"roles_supported":["physician","nurse"]},
        "transparency":{"shows_rationale":True,"links_to_evidence":True,"explainability":False},
        "fatigue":{"tiering":"moderate","silence_rules":True,"require_override_reason":True,"observed_override_rate_pct":20},
        "monitoring":{"has_kpis":True,"dashboard":True,"retrain_days":150,"incident_process":True},
        "governance":{"owner":"Owner","versioning":True,"change_control":True,"privacy_security_ok":True}
    }
    yml = tmp_path / "cli_spec.yaml"
    yml.write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")
    cmd = [sys.executable, "-m", "cds10_aidh.cli", "--spec", str(yml)]
    cp = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "total" in cp.stdout.lower()
