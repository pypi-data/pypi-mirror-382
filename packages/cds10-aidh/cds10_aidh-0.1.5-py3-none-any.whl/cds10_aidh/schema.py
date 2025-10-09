
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

class Delivery(BaseModel):
    timing: Literal["real-time","near-real-time","batch"] = "near-real-time"
    location: Literal["in-EHR","external","email","sms"] = "external"
    latency_ms: Optional[int] = None

class Actionability(BaseModel):
    has_recommendation: bool = False
    one_click: bool = False
    has_order_set: bool = False

class DataEntry(BaseModel):
    auto_fetch_pct: Optional[float] = None
    manual_fields: Optional[int] = None

class DefaultsSafety(BaseModel):
    smart_defaults: bool = False
    opt_out_when_safe: bool = False
    safety_rails: bool = False

class Proactivity(BaseModel):
    triggers: List[str] = []
    proactive: bool = False

class TeamScope(BaseModel):
    roles_supported: List[str] = []

class Transparency(BaseModel):
    shows_rationale: bool = False
    links_to_evidence: bool = False
    explainability: bool = False

class Fatigue(BaseModel):
    tiering: Optional[Literal["low","moderate","high"]] = None
    silence_rules: bool = False
    require_override_reason: bool = False
    observed_override_rate_pct: Optional[float] = None

class Monitoring(BaseModel):
    has_kpis: bool = False
    dashboard: bool = False
    retrain_days: Optional[int] = None
    incident_process: bool = False

class Workflow(BaseModel):
    stages: List[str] = []
    click_count_to_act: Optional[int] = None

class Governance(BaseModel):
    owner: Optional[str] = None
    versioning: bool = False
    change_control: bool = False
    privacy_security_ok: bool = False

class CDSInput(BaseModel):
    name: str
    workflow: Workflow = Workflow()
    delivery: Delivery = Delivery()
    actionability: Actionability = Actionability()
    data_entry: DataEntry = DataEntry()
    defaults_safety: DefaultsSafety = DefaultsSafety()
    proactivity: Proactivity = Proactivity()
    team_scope: TeamScope = TeamScope()
    transparency: Transparency = Transparency()
    fatigue: Fatigue = Fatigue()
    monitoring: Monitoring = Monitoring()
    governance: Governance = Governance()
    extra: Dict[str, Any] = Field(default_factory=dict)
