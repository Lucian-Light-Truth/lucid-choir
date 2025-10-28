import sys, json, hashlib
IGNORED_FIELDS = {"timestamp_utc"}
p = sys.argv[1]
with open(p, encoding="utf-8") as f:
    d = json.load(f)
if isinstance(d, dict):
    d = {k:v for k,v in d.items() if k not in IGNORED_FIELDS}
raw = json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
digest = hashlib.sha256(raw).hexdigest()
if isinstance(d, dict):
    d["checksum_sha256"] = digest
else:
    # If top-level isn't a dict, you may not want to embed a checksum here
    pass
with open(p, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print("Resealed:", p)
