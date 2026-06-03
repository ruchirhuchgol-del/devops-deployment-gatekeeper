"""
DevSecOps Deployment Gatekeeper — Mock Demo Runner
Simulates a full security gate run with realistic fake data.
Run with: python demo_runner.py
"""

import json
import time
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

# ── Colour helpers ──────────────────────────────────────────────────────────
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def banner(text, colour=BOLD):
    width = 60
    print(f"\n{colour}{'═' * width}{RESET}")
    print(f"{colour}  {text}{RESET}")
    print(f"{colour}{'═' * width}{RESET}\n")

def step(num, label):
    print(f"{CYAN}{BOLD}[{num}/4]{RESET} {BOLD}{label}{RESET}")
    time.sleep(0.8)

def tick(label, value=""):
    print(f"  {GREEN}✓{RESET}  {label}", f"{CYAN}{value}{RESET}" if value else "")
    time.sleep(0.3)

def warn(label):
    print(f"  {YELLOW}⚠{RESET}  {label}")

def block(label):
    print(f"  {RED}✗{RESET}  {label}")


# ── Scenario selector ───────────────────────────────────────────────────────
SCENARIOS = {
    "1": {
        "name": "Clean PR — no vulnerabilities",
        "pr_number": "42",
        "title": "feat: add user authentication middleware",
        "author": "alice",
        "files_changed": 6,
        "additions": 183,
        "deletions": 12,
        "critical": 0, "major": 1, "minor": 3, "info": 4,
        "score": 91.0,
        "decision": "ALLOW",
        "issues": [],
    },
    "2": {
        "name": "Blocked PR — critical SQL injection",
        "pr_number": "87",
        "title": "fix: optimise database query performance",
        "author": "bob",
        "files_changed": 3,
        "additions": 67,
        "deletions": 8,
        "critical": 2, "major": 4, "minor": 7, "info": 2,
        "score": 34.5,
        "decision": "BLOCK",
        "issues": [
            {"type": "SQL Injection",       "severity": "CRITICAL", "file": "src/db/queries.py",      "line": 134, "cwe": "CWE-89"},
            {"type": "Hardcoded Password",  "severity": "CRITICAL", "file": "src/config/database.py", "line": 22,  "cwe": "CWE-798"},
            {"type": "XSS Vulnerability",   "severity": "MAJOR",    "file": "src/api/handlers.py",    "line": 78,  "cwe": "CWE-79"},
            {"type": "Missing Auth Check",  "severity": "MAJOR",    "file": "src/api/admin.py",       "line": 45,  "cwe": "CWE-306"},
        ],
    },
    "3": {
        "name": "Borderline PR — just under threshold",
        "pr_number": "103",
        "title": "refactor: migrate legacy payment module",
        "author": "carol",
        "files_changed": 14,
        "additions": 412,
        "deletions": 389,
        "critical": 0, "major": 3, "minor": 9, "info": 6,
        "score": 72.0,
        "decision": "ALLOW",
        "issues": [
            {"type": "Insecure Deserialization", "severity": "MAJOR", "file": "src/payment/processor.py", "line": 201, "cwe": "CWE-502"},
        ],
    },
}


def run_demo(scenario: dict):
    banner(f"DevSecOps Deployment Gatekeeper — Live Demo", BOLD)
    print(f"  Scenario : {BOLD}{scenario['name']}{RESET}")
    print(f"  PR       : #{scenario['pr_number']}  \"{scenario['title']}\"")
    print(f"  Author   : @{scenario['author']}")
    print(f"  Started  : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")

    # ── Agent 1: PR Metadata ─────────────────────────────────────────────────
    step(1, "PR Metadata Extraction Specialist")
    tick("Connected to GitHub API")
    tick("Fetched pull request", f"#{scenario['pr_number']}")
    tick("Files changed",        str(scenario['files_changed']))
    tick("Lines added",          f"+{scenario['additions']}")
    tick("Lines removed",        f"-{scenario['deletions']}")
    tick("Branch target",        "main")
    tick("Metadata packaged and passed to Scanner Agent")

    # ── Agent 2: SonarQube Scanner ───────────────────────────────────────────
    print()
    step(2, "SonarQube Security Scanner Agent")
    tick("sonar-scanner triggered for project")
    print(f"\n  {YELLOW}Waiting for analysis to complete...{RESET}")
    for i in range(1, 5):
        time.sleep(0.5)
        print(f"  {CYAN}  polling... attempt {i}/4{RESET}")
    print()
    tick("Scan completed successfully")
    tick("Issues retrieved (all pages)")
    tick("Critical vulnerabilities", str(scenario['critical']))
    tick("Major vulnerabilities",    str(scenario['major']))
    tick("Minor vulnerabilities",    str(scenario['minor']))
    tick("Security score",           f"{scenario['score']}/100")

    if scenario['issues']:
        print(f"\n  {RED}{BOLD}  Vulnerabilities found:{RESET}")
        for issue in scenario['issues']:
            sev_colour = RED if issue['severity'] == 'CRITICAL' else YELLOW
            print(f"    {sev_colour}[{issue['severity']}]{RESET}  "
                  f"{issue['type']} — {issue['file']}:{issue['line']}  "
                  f"{CYAN}({issue['cwe']}){RESET}")

    # ── Agent 3: Policy Decision ─────────────────────────────────────────────
    print()
    step(3, "Security Policy Decision Engine")
    tick("PolicyEvaluator loaded (critical threshold = 0)")
    tick("CWE high-risk set checked (CWE-79, 89, 200, 352, 502)")

    if scenario['decision'] == "BLOCK":
        block(f"Critical threshold exceeded — {scenario['critical']} critical issue(s) found")
        block(f"Security score {scenario['score']} < 70 threshold")
        print()
        print(f"  {RED}{BOLD}  DECISION: ❌  BLOCK{RESET}")
        print(f"  {RED}  Deployment will NOT proceed{RESET}")
    else:
        tick("No policy violations detected")
        tick(f"Security score {scenario['score']} ≥ 70 threshold")
        print()
        print(f"  {GREEN}{BOLD}  DECISION: ✅  ALLOW{RESET}")
        print(f"  {GREEN}  Deployment approved to proceed{RESET}")

    # ── Agent 4: Notifications ───────────────────────────────────────────────
    print()
    step(4, "Security Alert Notification Manager")

    if scenario['decision'] == "BLOCK":
        msg = (f"❌ *Deployment BLOCKED* — PR #{scenario['pr_number']}\n"
               f"   Repository  : acme-corp/backend\n"
               f"   Author      : @{scenario['author']}\n"
               f"   Critical    : {scenario['critical']}  |  Major: {scenario['major']}\n"
               f"   Score       : {scenario['score']}/100\n"
               f"   Action      : Fix critical vulnerabilities before re-requesting review")
    else:
        msg = (f"✅ *Deployment APPROVED* — PR #{scenario['pr_number']}\n"
               f"   Repository  : acme-corp/backend\n"
               f"   Author      : @{scenario['author']}\n"
               f"   Score       : {scenario['score']}/100\n"
               f"   Action      : Safe to merge and deploy")

    print(f"  {BLUE}  Slack message dispatched to #security-alerts:{RESET}")
    print()
    for line in msg.split('\n'):
        print(f"    {line}")
    print()
    tick("GitHub PR status check updated")
    tick(f"PR #{scenario['pr_number']} marked as",
         "FAILED — blocked by security gate" if scenario['decision'] == "BLOCK"
         else "PASSED — security gate approved")

    # ── Summary ──────────────────────────────────────────────────────────────
    colour = GREEN if scenario['decision'] == "ALLOW" else RED
    banner(f"Gate Result: {scenario['decision']}", colour)
    print(f"  PR          #{scenario['pr_number']}  |  {scenario['title']}")
    print(f"  Author      @{scenario['author']}")
    print(f"  Score       {scenario['score']}/100")
    print(f"  Critical    {scenario['critical']}  |  Major: {scenario['major']}  |  Minor: {scenario['minor']}")
    print(f"  Decision    {colour}{BOLD}{scenario['decision']}{RESET}")
    print(f"  Duration    ~{2.3 + len(scenario['issues']) * 0.1:.1f}s  (simulated)\n")


def main():
    print(f"\n{BOLD}DevSecOps Deployment Gatekeeper — Demo{RESET}")
    print("Choose a scenario:\n")
    for key, s in SCENARIOS.items():
        print(f"  {CYAN}[{key}]{RESET}  {s['name']}")
    print()

    choice = input("Enter 1, 2, or 3 (default 2): ").strip() or "2"
    if choice not in SCENARIOS:
        print("Invalid choice, using scenario 2.")
        choice = "2"

    run_demo(SCENARIOS[choice])


if __name__ == "__main__":
    main()