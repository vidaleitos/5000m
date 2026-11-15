---
name: garmin-mcp-setup
description: "Garmin MCP setup/auth on Windows: python venv, env-var auth."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Garmin, MCP, Python, Auth, RateLimit]
    related_skills: [garmin-mcp]
---

# Garmin MCP — Setup & Auth on Windows

Setup and authentication for `garmin-mcp-unofficial` (the local-first Garmin Connect MCP server; skill reference: hub skill `garmin-mcp`). Covers the Python-helper pitfalls and Garmin's headless-login blocking, which are the two things that actually go wrong.

## Setup

```bash
HTTPS_PROXY=http://127.0.0.1:7897 npx -y garmin-mcp-unofficial setup   # creates ~/.garmin-mcp/config.json (credentials never written to MCP config)
```

Add to Hermes (stdio shape from the skill's generic.json):

```bash
echo y | hermes mcp add garmin-mcp --command npx --args -y garmin-mcp-unofficial   # 42 tools, Confirm prompt needs echo y
```

## Auth: the Python helper (`auth --use-python`)

The Node headless login often gets Cloudflare-challenged/rate-limited; the fallback is the Python `garminconnect` helper:

```bash
npx -y garmin-mcp-unofficial auth --use-python
```

**Hard requirements discovered the hard way:**

1. **Python 3.11+ required** — `garminconnect` pulls `curl_cffi`, which imports `typing.Unpack` (Python 3.11+). A 3.10 interpreter fails with `ImportError: cannot import name 'Unpack' from 'typing'` → helper reports "curl_cffi not available".
2. **The helper uses the FIRST `python` on PATH** — on this machine that's the Hermes venv python, which has NO pip (`No module named pip`). Fix: build a dedicated venv and put it FIRST on PATH:

```powershell
uv venv --python 3.12 C:\Users\<user>\.garmin-mcp\venv
C:\Users\<user>\.garmin-mcp\venv\Scripts\python.exe -m pip install garminconnect curl_cffi
# then, before auth:
$env:Path="C:\Users\<user>\.garmin-mcp\venv\Scripts;" + $env:Path
```

(uv-installed pythons may lack pip; a `uv venv` + its bundled pip works, or `uv pip install --python <venv-python>`.)

3. **Non-interactive auth**: the CLI reads env vars instead of prompting:

```powershell
$env:GARMIN_EMAIL='<email>'
$env:GARMIN_PASSWORD='<password>'      # single quotes = literal, safe for special chars
npx.cmd -y garmin-mcp-unofficial auth --use-python   # npx.cmd: PowerShell blocks npx.ps1 (execution policy)
```

(`GARMIN_MFA_CODE` if 2FA prompts.) Never paste Garmin credentials into chat — the user runs auth in their own terminal.

## Garmin-side blocking (the part you cannot fix locally)

- **429 "IP rate limited"** on mobile endpoints — after repeated attempts Garmin rate-limits by IP; switching to a different egress (Clash proxy node) helps, but the portal endpoint may still be the one that answers.
- **401 "Invalid Username or Password" from the portal strategy even with correct credentials** = the ACCOUNT is temporarily locked for headless/automated logins (repeated failed automated attempts). Browser login at connect.garmin.com still works with the same creds — use that as the ground-truth check: browser OK + automated 401 ⇒ lockout, not wrong password.
- Lockout can outlast a 30–60 min cooldown; each retry may extend it. Best sequence: verify creds in browser → wait (30–60 min) → ONE attempt → if 401 again, wait hours.
- A successful browser login often clears/resets the lock — retry the automated flow ~15–30 min after a successful browser login.

## Verified state (Aug 2026)

Setup, venv, env-var auth, MCP registration all verified working. The login itself remained blocked by Garmin-side lockout (401) at session end — retry after cooldown; do not re-debug the environment.
