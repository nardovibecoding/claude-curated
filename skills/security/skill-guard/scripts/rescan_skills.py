#!/usr/bin/env python3
# Copyright (c) 2026 Nardo. AGPL-3.0 — see LICENSE
"""
Skill Rescan — detect changed skills and re-audit them.

Maintains a checksum baseline of all installed skills.
On each run, compares current state to baseline.
Changed/new skills get audited via skill_security_auditor.py.

Usage:
    python3 rescan_skills.py                # scan changed + new skills
    python3 rescan_skills.py --full         # force full rescan of all skills
    python3 rescan_skills.py --report       # show last scan results

Exit codes:
    0 = all clean
    1 = at least one FAIL verdict
    2 = at least one WARN verdict (no FAILs)
"""

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILLS_DIR = Path.home() / ".claude" / "skills"
AUDITOR_SCRIPT = Path(__file__).parent / "skill_security_auditor.py"
BASELINE_FILE = Path.home() / ".claude" / "skill_checksums.json"
REPORT_FILE = Path.home() / ".claude" / "skill_rescan_report.json"

# Skills that legitimately contain patterns they scan for (self-referential)
# or use flagged APIs as core functionality (e.g. browsers use child_process)
WHITELIST = {
    "skillguard",  # contains detection patterns + threat model examples
    "browse",                  # headless browser needs child_process
    "extractskill",            # references injection patterns in documentation
}


def hash_skill_dir(skill_path: Path) -> str:
    """SHA-256 hash of all file contents in a skill directory."""
    h = hashlib.sha256()
    for root, _dirs, files in sorted(os.walk(skill_path)):
        for fname in sorted(files):
            fpath = Path(root) / fname
            if fpath.name.startswith("."):
                continue
            try:
                h.update(fpath.read_bytes())
                h.update(str(fpath.relative_to(skill_path)).encode())
            except (OSError, PermissionError):
                continue
    return h.hexdigest()


def load_baseline() -> dict:
    if BASELINE_FILE.exists():
        return json.loads(BASELINE_FILE.read_text())
    return {}


def save_baseline(baseline: dict):
    BASELINE_FILE.write_text(json.dumps(baseline, indent=2))


def audit_skill(skill_path: Path) -> dict:
    """Run the auditor on a single skill, return JSON result."""
    try:
        result = subprocess.run(
            [sys.executable, str(AUDITOR_SCRIPT), str(skill_path), "--json"],
            capture_output=True, text=True, timeout=30,
        )
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
        return {
            "skill_name": skill_path.name,
            "skill_path": str(skill_path),
            "verdict": "ERROR",
            "error": str(e),
        }


def main():
    full_scan = "--full" in sys.argv
    report_only = "--report" in sys.argv

    if report_only:
        if REPORT_FILE.exists():
            report = json.loads(REPORT_FILE.read_text())
            print(f"Last scan: {report.get('timestamp', 'unknown')}")
            print(f"Skills scanned: {report.get('scanned', 0)}")
            print(f"Verdicts: {json.dumps(report.get('verdicts', {}), indent=2)}")
            for r in report.get("results", []):
                verdict = r.get("verdict", "?")
                icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "ERROR": "💥"}.get(verdict, "?")
                print(f"  {icon} {r.get('skill_name', '?')} → {verdict}")
                if verdict in ("FAIL", "WARN"):
                    for f in r.get("findings", []):
                        if f.get("severity") in ("CRITICAL", "HIGH"):
                            print(f"     {f['severity']}: {f.get('risk', '')[:80]}")
        else:
            print("No previous scan found. Run without --report first.")
        return 0

    if not SKILLS_DIR.exists():
        print("No skills directory found.")
        return 0

    baseline = load_baseline()
    skills_to_scan = []
    new_baseline = {}

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        # Skip disabled skills
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        current_hash = hash_skill_dir(skill_dir)
        new_baseline[skill_dir.name] = current_hash

        if full_scan:
            skills_to_scan.append(skill_dir)
        elif skill_dir.name not in baseline:
            print(f"🆕 New skill: {skill_dir.name}")
            skills_to_scan.append(skill_dir)
        elif baseline[skill_dir.name] != current_hash:
            print(f"🔄 Changed: {skill_dir.name}")
            skills_to_scan.append(skill_dir)

    # Detect removed skills
    for old_name in baseline:
        if old_name not in new_baseline:
            print(f"🗑️  Removed: {old_name}")

    if not skills_to_scan:
        print(f"✅ All {len(new_baseline)} skills unchanged. No audit needed.")
        save_baseline(new_baseline)
        return 0

    print(f"\nScanning {len(skills_to_scan)} skill(s)...\n")

    results = []
    verdicts = {"PASS": 0, "WARN": 0, "FAIL": 0, "ERROR": 0}
    worst_exit = 0

    for skill_dir in skills_to_scan:
        if skill_dir.name in WHITELIST:
            print(f"  Auditing {skill_dir.name}... ⏭️  WHITELISTED")
            results.append({"skill_name": skill_dir.name, "verdict": "PASS", "whitelisted": True})
            verdicts["PASS"] += 1
            continue

        print(f"  Auditing {skill_dir.name}...", end=" ", flush=True)
        result = audit_skill(skill_dir)
        verdict = result.get("verdict", "ERROR")
        verdicts[verdict] = verdicts.get(verdict, 0) + 1
        results.append(result)

        icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "ERROR": "💥"}.get(verdict, "?")
        findings_summary = ""
        summary = result.get("summary", {})
        if summary.get("critical", 0) > 0 or summary.get("high", 0) > 0:
            findings_summary = f" ({summary.get('critical', 0)}C/{summary.get('high', 0)}H)"
        print(f"{icon} {verdict}{findings_summary}")

        if verdict == "FAIL":
            worst_exit = max(worst_exit, 1)
            # Print critical findings
            for f in result.get("findings", []):
                if f.get("severity") == "CRITICAL":
                    print(f"     🔴 {f.get('category', '')}: {f.get('risk', '')[:80]}")
                    print(f"        {f.get('file', '')}:{f.get('line', '')}")
        elif verdict == "WARN":
            worst_exit = max(worst_exit, 2)

    # Save report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scanned": len(skills_to_scan),
        "total_skills": len(new_baseline),
        "verdicts": verdicts,
        "results": results,
    }
    REPORT_FILE.write_text(json.dumps(report, indent=2))

    # Save updated baseline
    save_baseline(new_baseline)

    # Summary
    print(f"\n{'='*50}")
    print(f"Scanned: {len(skills_to_scan)} | "
          f"PASS: {verdicts['PASS']} | WARN: {verdicts['WARN']} | "
          f"FAIL: {verdicts['FAIL']} | ERROR: {verdicts['ERROR']}")

    if verdicts["FAIL"] > 0:
        print("\n❌ FAILED skills found — review immediately!")
    elif verdicts["WARN"] > 0:
        print("\n⚠️  Warnings found — review before use.")
    else:
        print("\n✅ All scanned skills passed.")

    return worst_exit


if __name__ == "__main__":
    sys.exit(main())
