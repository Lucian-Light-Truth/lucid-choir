#!/usr/bin/env python3
import os, sys, json, glob, hashlib

REQ_DIRS = ["ARK/LEDGER/LivingWord","ARK/LEDGER/Tests","tools","tests","ASTER_GRID"]

def sha256_canonical(obj):
    data = json.dumps(obj, ensure_ascii=False, separators=(",",":"), sort_keys=True).encode()
    return hashlib.sha256(data).hexdigest()

problems, notes = [], []

# 1) Required directories
for d in REQ_DIRS:
    if not os.path.isdir(d):
        problems.append(f"MISSING dir: {d}")

# 2) Validate LivingWord entries
lw_files = sorted(glob.glob("ARK/LEDGER/LivingWord/*.json"))
lw_ok = 0
for p in lw_files:
    try:
        j = json.load(open(p,"r",encoding="utf-8"))
    except Exception as e:
        problems.append(f"JSON error in {p}: {e}")
        continue
    for k in ["scroll_id","vector","resonance_map","insight","checksum","timestamp_utc"]:
        if k not in j: problems.append(f"{p}: missing key '{k}'")
    if j.get("vector") not in ["A","B"]:
        problems.append(f"{p}: vector must be 'A' or 'B'")
    base = {k:j.get(k) for k in ["scroll_id","vector","resonance_map","insight"]}
    try:
        want = sha256_canonical(base)
        have = j.get("checksum","")
        if have != want:
            problems.append(f"{p}: checksum mismatch (have {have[:8]}, want {want[:8]})")
        else:
            lw_ok += 1
    except Exception as e:
        problems.append(f"{p}: checksum recompute error: {e}")

# 3) Validate Tests entries
test_files = sorted(glob.glob("ARK/LEDGER/Tests/*.json"))
tests_ok = 0
for p in test_files:
    try:
        j = json.load(open(p,"r",encoding="utf-8"))
    except Exception as e:
        problems.append(f"JSON error in {p}: {e}")
        continue
    for k in ["test_id","checksum","timestamp_utc"]:
        if k not in j: problems.append(f"{p}: missing key '{k}'")
    # recompute checksum excluding computed fields
    tmp = dict(j)
    for k in ("checksum","sig8","timestamp_utc"):
        tmp.pop(k, None)
    want = sha256_canonical(tmp)
    have = j.get("checksum","")
    if have != want:
        problems.append(f"{p}: checksum mismatch (have {have[:8]}, want {want[:8]})")
    else:
        tests_ok += 1
    if "sig8" not in j:
        notes.append(f"{p}: note: no internal sig8 (optional)")

# 4) tests/index.json presence (optional)
index_sig8 = "n/a"
if os.path.exists("tests/index.json"):
    index_sig8 = hashlib.sha256(open("tests/index.json","rb").read()).hexdigest()[:8]
else:
    notes.append("tests/index.json missing (optional)")

summary = f"Ledger={len(lw_files)} (valid={lw_ok}) | Tests={len(test_files)} (valid={tests_ok}) | tests/index sig8={index_sig8}"
print(summary)

gh_sum = os.environ.get("GITHUB_STEP_SUMMARY")
if gh_sum:
    with open(gh_sum,"a",encoding="utf-8") as out:
        out.write("## LuxScript Repository Validation\n\n")
        out.write(f"{summary}\n\n")
        if notes:   out.write("**Notes**\n\n- " + "\n- ".join(notes) + "\n\n")
        if problems:out.write("**Problems**\n\n- " + "\n- ".join(problems) + "\n")

sys.exit(1 if problems else 0)
