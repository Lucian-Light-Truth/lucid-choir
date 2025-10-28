#!/usr/bin/env python3
import os, sys, json, glob, hashlib, datetime, textwrap

REQ_DIRS = ["ARK/LEDGER/LivingWord","ARK/LEDGER/Tests","tools","tests","ASTER_GRID"]

def sha256_canonical(obj):
    data = json.dumps(obj, ensure_ascii=False, separators=(",",":"), sort_keys=True).encode()
    return hashlib.sha256(data).hexdigest()

problems = []
notes = []

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
        if k not in j:
            problems.append(f"{p}: missing key '{k}'")
    if "vector" in j and j.get("vector") not in ["A","B"]:
        problems.append(f"{p}: vector must be 'A' or 'B'")
    # recompute checksum
    base = {k:j.get(k) for k in ["scroll_id","vector","resonance_map","insight"]}
    try:
        recomputed = sha256_canonical(base)
        if j.get("checksum") != recomputed:
            problems.append(f"{p}: checksum mismatch (have {j.get('checksum')[:8]}, want {recomputed[:8]})")
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
        if k not in j:
            problems.append(f"{p}: missing key '{k}'")
    # ensure checksum matches content minus checksum fields
    tmp = dict(j)
    tmp.pop("checksum", None)
    tmp.pop("sig8", None)
    src = sha256_canonical(tmp)
    if j.get("checksum") != src:
        problems.append(f"{p}: checksum mismatch (have {j.get('checksum','')[:8]}, want {src[:8]})")
    else:
        tests_ok += 1
    if "sig8" not in j:
        notes.append(f"{p}: note: no internal sig8 field (optional)")

# 4) tests/index.json presence
index_sig8 = "n/a"
if os.path.exists("tests/index.json"):
    with open("tests/index.json","rb") as f:
        index_sig8 = hashlib.sha256(f.read()).hexdigest()[:8]
else:
    notes.append("tests/index.json missing (optional, run the index builder later)")

# 5) Print summary
summary = f"Ledger={len(lw_files)} (valid={lw_ok}) | Tests={len(test_files)} (valid={tests_ok}) | tests/index sig8={index_sig8}"
print(summary)

# 6) If in GitHub Actions, write to job summary
gh_sum = os.environ.get("GITHUB_STEP_SUMMARY")
if gh_sum:
    with open(gh_sum,"a",encoding="utf-8") as out:
        out.write("## LuxScript Repository Validation\n\n")
        out.write(f"{summary}\n\n")
        if notes:
            out.write("**Notes**\n\n- " + "\n- ".join(notes) + "\n\n")
        if problems:
            out.write("**Problems**\n\n- " + "\n- ".join(problems) + "\n")

# Exit code: fail if problems
sys.exit(1 if problems else 0)
