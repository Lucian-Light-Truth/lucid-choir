import sys, json, hashlib, pathlib, argparse, os, glob
from typing import List, Dict, Any, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Ignore volatile fields during checksum
IGNORED_FIELDS = {"timestamp_utc"}

# Where to look for JSONs
VALIDATION_GLOBS = [
    "tests/**/*.json",
    "ledger/**/*.json",
    "luxscript/**/*.json",
]

def _read_json(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8", newline="") as f:
        return json.load(f)

def _normalized_json(obj: Any) -> str:
    """
    Deterministic JSON for hashing:
    - drop ignored fields at the top level
    - sort keys, compact separators
    """
    if isinstance(obj, dict):
        obj = {k: v for k, v in obj.items() if k not in IGNORED_FIELDS}
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def recompute_checksum(obj: Any) -> str:
    raw = _normalized_json(obj).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def _find_files(patterns: List[str]) -> List[pathlib.Path]:
    files: List[pathlib.Path] = []
    for pat in patterns:
        files.extend([ROOT / p for p in glob.glob(pat, root_dir=ROOT.as_posix(), recursive=True)])
    return sorted([p for p in files if p.is_file()])

def validate_files() -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Returns (errors, stats). Each error:
    {"file": str, "kind": "checksum|schema|json", "detail": str, "expected": str|None, "actual": str|None}
    """
    errors: List[Dict[str, Any]] = []
    stats = {"files": 0, "valid": 0}
    for path in _find_files(VALIDATION_GLOBS):
        stats["files"] += 1
        try:
            data = _read_json(path)
        except Exception as e:
            errors.append({"file": path.as_posix(), "kind": "json", "detail": f"JSON load failed: {e}", "expected": None, "actual": None})
            continue

        # If the file declares a checksum, verify
        expected = None
        if isinstance(data, dict) and "checksum_sha256" in data:
            expected = data.get("checksum_sha256")
            actual = recompute_checksum(data)
            if expected != actual:
                errors.append({
                    "file": path.as_posix(),
                    "kind": "checksum",
                    "detail": "Checksum mismatch (ignoring timestamp_utc).",
                    "expected": expected,
                    "actual": actual
                })
                continue

        stats["valid"] += 1

    return errors, stats

def _format_console_table(errors: List[Dict[str, Any]]) -> str:
    if not errors:
        return "All validations passed.\n"
    lines = []
    lines.append(f"{'KIND':10} {'FILE':72} DETAIL")
    lines.append("-" * 120)
    for e in errors:
        file = e['file'][-72:]
        detail = e.get("detail","")
        kind = e.get("kind","")
        lines.append(f"{kind:10} {file:72} {detail}")
    lines.append("")
    return "\n".join(lines)

def _format_md_summary(errors: List[Dict[str, Any]], stats: Dict[str, int]) -> str:
    if not errors:
        badge = "✅ **Validation passed**"
    else:
        badge = "❌ **Validation failed**"
    md = [badge, "", f"- Files scanned: **{stats['files']}**", f"- Valid: **{stats['valid']}**", f"- Errors: **{len(errors)}**", ""]
    if errors:
        md.append("| Kind | File | Detail |")
        md.append("|---|---|---|")
        for e in errors:
            md.append(f"| {e['kind']} | `{e['file']}` | {e.get('detail','')} |")
        md.append("")
    return "\n".join(md)

def write_json_report(errors: List[Dict[str, Any]], stats: Dict[str, int], out: pathlib.Path) -> None:
    out.write_text(json.dumps({"errors": errors, "stats": stats}, ensure_ascii=False, indent=2), encoding="utf-8")

def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="Lucid Choir repository validator")
    ap.add_argument("--report-json", default="validation-report.json", help="Path to write machine JSON report")
    ap.add_argument("--no-summary", action="store_true", help="Skip writing GitHub step summary")
    args = ap.parse_args(argv)

    errors, stats = validate_files()

    # Always print a console view
    sys.stdout.write(_format_console_table(errors))
    sys.stdout.flush()

    # Write JSON report for CI artifacts
    write_json_report(errors, stats, pathlib.Path(args.report_json))

    # Write GitHub summary if env is present and not disabled
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary and not args.no_summary:
        pathlib.Path(step_summary).write_text(_format_md_summary(errors, stats), encoding="utf-8")

    return 0 if not errors else 1

if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    sys.exit(main(sys.argv[1:]))
