import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
for p in sorted(ROOT.glob('ARK/LEDGER/Tests/Session_*/*_*.json')):
    d = json.load(open(p,encoding='utf-8'))
    m = d.get('metrics') or {}
    if not isinstance(m, dict): m = {}
    # RDS: prefer coherence if RDS absent
    if 'RDS' not in m:
        rds = m.get('coherence', 0.0)
        try: rds = float(rds)
        except: rds = 0.0
        m['RDS'] = rds
    # Defaults for MFR/AGC if missing
    if 'MFR' not in m:
        m['MFR'] = 0.0
    if 'AGC' not in m:
        m['AGC'] = 0.0
    d['metrics'] = m
    json.dump(d, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
    print("Backfilled:", p)
