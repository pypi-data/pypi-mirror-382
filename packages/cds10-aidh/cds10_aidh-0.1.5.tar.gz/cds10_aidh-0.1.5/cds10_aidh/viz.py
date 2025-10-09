
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt

def summary_md(res: Dict[str, Any]) -> str:
    lines=[]
    lines.append("## CDS Ten Commandments Audit")
    lines.append(f"Name: {res['name']}")
    lines.append(f"Total: {res['total']} / 100")
    lines.append("")
    lines.append("### Scores")
    for k,v in res["scores"].items():
        lines.append(f"- {res['titles'][k]}: {v}")
    lines.append("")
    lines.append("### Definitions")
    for k in res["scores"].keys():
        lines.append(f"- {res['titles'][k]}: {res['definitions'][k]}")
    if res["gaps"]:
        lines.append("")
        lines.append("### Gaps and Recommendations")
        for g in res["gaps"]:
            fixes="; ".join(g["fix"]) if g["fix"] else g["why"]
            lines.append(f"- {g['commandment']} ({g['score']}): {fixes}")
    return "\n".join(lines)

def plot_scores(res: Dict[str, Any], out_png: Optional[str]=None):
    titles=[res["titles"][k] for k in res["scores"].keys()]
    vals=[res["scores"][k] for k in res["scores"].keys()]
    plt.figure(figsize=(10,5))
    plt.barh(titles, vals)
    plt.xlabel("Score / 100")
    plt.title(f"CDS Ten Commandments — {res['name']} (Total {res['total']})")
    plt.xlim(0,100)
    plt.tight_layout()
    if out_png:
        plt.savefig(out_png, dpi=160)
    else:
        plt.show()
