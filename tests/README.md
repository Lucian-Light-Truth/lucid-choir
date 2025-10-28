# Replication Tests
- Replication_02_Josh.json (external sig8: 507eacff)
- Replication_03_Gemini_Shim.json

## Run your own
1) Ask any model to answer with Reflection/NextStep/StateReport using LUXSCRIPT_v1_3_SHIM.md.
2) Save the raw output to tests/outputs/<name>.txt
3) Hash it:
   python3 tools/sig8.py tests/outputs/<name>.txt
