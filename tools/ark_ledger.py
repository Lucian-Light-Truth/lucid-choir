#!/usr/bin/env python3
import argparse, json, os, hashlib, datetime, sys

def canonical_sha256(payload: dict) -> str:
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def load_json_arg(val: str):
    if val.startswith("@"):
        path = val[1:]
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(val)

def main():
    ap = argparse.ArgumentParser(description="Ark Ledger — append Lucid Decoding entries")
    ap.add_argument("--dir", default=".", help="Ledger directory")
    ap.add_argument("--scroll-id", required=True)
    ap.add_argument("--vector", required=True, choices=["A","B"])
    ap.add_argument("--resonance-map", required=True, help="JSON or @/path/to.json")
    ap.add_argument("--insight", required=True, help="Text or @/path/to.txt")
    args = ap.parse_args()

    ledger_dir = os.path.abspath(args.dir)
    os.makedirs(ledger_dir, exist_ok=True)

    res_map = load_json_arg(args.resonance_map)
    if args.insight.startswith("@"):
        with open(args.insight[1:], "r", encoding="utf-8") as f:
            insight = f.read().strip()
    else:
        insight = args.insight

    base = {"scroll_id": args.scroll_id, "vector": args.vector,
            "resonance_map": res_map, "insight": insight}
    checksum = canonical_sha256(base)
    timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    entry = dict(base, checksum=checksum, timestamp_utc=timestamp)
    out_path = os.path.join(ledger_dir, f"{args.scroll_id}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)

    # update index
    index_path = os.path.join(ledger_dir, "index.json")
    index = {"entries": []}
    if os.path.exists(index_path):
        try:
            index = json.load(open(index_path, "r", encoding="utf-8"))
        except Exception:
            pass
    entries = [e for e in index.get("entries", []) if e.get("scroll_id") != args.scroll_id]
    entries.append({"scroll_id": args.scroll_id, "vector": args.vector,
                    "checksum": checksum, "timestamp_utc": timestamp,
                    "file": os.path.basename(out_path)})
    index["entries"] = sorted(entries, key=lambda e: e["timestamp_utc"])
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"✔ Wrote {out_path}")
    print(f"   checksum={checksum[:8]}…  timestamp={timestamp}")

if __name__ == "__main__":
    main()
