#!/usr/bin/env python3
import sys, json, hashlib, datetime
def readall(path):
    if path == "-" or path == "":
        return sys.stdin.read().encode("utf-8")
    return open(path, "rb").read()
data = readall(sys.argv[1] if len(sys.argv)>1 else "-")
h = hashlib.sha256(data).hexdigest()
print(json.dumps({
  "sha256": h,
  "sig8": h[:8],
  "timestamp_utc": datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
}, indent=2))
