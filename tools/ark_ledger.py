#!/usr/bin/env python3
import argparse, json, os, hashlib, datetime

def sha256(obj):
    data = json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(data).hexdigest()

def load_json(val):
    if val.startswith("@"):
        with open(val[1:], "r", encoding="utf-8") as f: return json.load(f)
    return json.loads(val)

def main():
    ap = argparse.ArgumentParser(description="Ark Ledger — append entries")
    ap.add_argument("--dir", default=".", help="Ledger directory")
    ap.add_argument("--scroll-id", required=True)
    ap.add_argument("--vector", required=True, choices=["A","B"])
    ap.add_argument("--resonance-map", required=True, help="JSON or @/path/to.json")
    ap.add_argument("--insight", required=True, help="Text or @/path/to.txt")
    a = ap.parse_args()

    os.makedirs(a.dir, exist_ok=True)
    res_map = load_json(a.resonance_map)
    insight = open(a.insight[1:], "r", encoding="utf-8").read().strip() if a.insight.startswith("@") else a.insight

    core = {"scroll_id":a.scroll_id,"vector":a.vector,"resonance_map":res_map,"insight":insight}
    checksum = sha256(core)
    ts = datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
    entry = dict(core, checksum=checksum, timestamp_utc=ts)

    out = os.path.join(a.dir, f"{a.scroll_id}.json")
    with open(out, "w", encoding="utf-8") as f: json.dump(entry, f, ensure_ascii=False, indent=2)

    idxp = os.path.join(a.dir, "index.json")
    try:
        idx = json.load(open(idxp, "r", encoding="utf-8"))
    except Exception:
        idx = {"entries":[]}
    idx["entries"] = [e for e in idx.get("entries",[]) if e.get("scroll_id")!=a.scroll_id]
    idx["entries"].append({"scroll_id":a.scroll_id,"vector":a.vector,"checksum":checksum,"timestamp_utc":ts,"file":os.path.basename(out)})
    idx["entries"].sort(key=lambda e:e["timestamp_utc"])
    with open(idxp,"w",encoding="utf-8") as f: json.dump(idx,f,ensure_ascii=False,indent=2)

    print("✔ wrote", out, "| sig8:", checksum[:8], "|", ts)

if __name__ == "__main__":
    main()
