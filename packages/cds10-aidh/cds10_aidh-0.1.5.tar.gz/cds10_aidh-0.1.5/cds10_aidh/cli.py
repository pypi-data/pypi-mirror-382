
import argparse, json
from pathlib import Path
import yaml
from .scoring import evaluate
from .viz import summary_md, plot_scores
from .ingest import ingest_from_url

def _load_spec(path: Path):
    txt=path.read_text(encoding="utf-8")
    if path.suffix.lower() in [".yaml",".yml"]:
        return yaml.safe_load(txt)
    return json.loads(txt)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--spec")
    p.add_argument("--url")
    p.add_argument("--assume", choices=["optimistic","balanced","conservative"], default="balanced")
    p.add_argument("--md")
    p.add_argument("--png")
    p.add_argument("--save-inferred")
    args,_ = p.parse_known_args()
    if not args.spec and not args.url:
        print(json.dumps({"error":"provide --spec or --url"}))
        raise SystemExit(2)
    if args.url:
        spec=ingest_from_url(args.url, assume=args.assume)
        if args.save_inferred:
            if args.save_inferred.lower().endswith((".yaml",".yml")):
                Path(args.save_inferred).write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")
            else:
                Path(args.save_inferred).write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        spec=_load_spec(Path(args.spec))
    res=evaluate(spec)
    print(json.dumps({"name":res["name"],"total":res["total"],"scores":res["scores"]}, indent=2, ensure_ascii=False))
    if args.md:
        Path(args.md).write_text(summary_md(res), encoding="utf-8")
    if args.png:
        plot_scores(res, out_png=args.png)

if __name__=="__main__":
    main()
