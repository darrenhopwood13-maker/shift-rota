#!/usr/bin/env python3
"""Publish the shift rota to GitHub Pages under darrenhopwood13-maker."""
import json
import os
import pathlib
import subprocess
import time
import urllib.error
import urllib.request

BASE = pathlib.Path("/root/outputs/shift-rota")
REPO = "shift-rota"
OWNER = "darrenhopwood13-maker"

# --- token from the profile .env, never printed ---
tok = None
for line in pathlib.Path("/root/.hermes/profiles/banksy/.env").read_text().splitlines():
    if line.startswith("GITHUB_TOKEN="):
        tok = line.split("=", 1)[1].strip().strip('"').strip("'")
assert tok, "no GITHUB_TOKEN"

H = {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json",
     "User-Agent": "banksy-rota"}


def api(method, path, body=None):
    req = urllib.request.Request(
        "https://api.github.com" + path, method=method, headers=H,
        data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


# --- repo ---
st, js = api("GET", f"/repos/{OWNER}/{REPO}")
if st == 404:
    st, js = api("POST", "/user/repos",
                 {"name": REPO, "private": False, "auto_init": False,
                  "description": "Shift rota - 6 month, 3 staff, Mon-Fri early/late + Saturday rotation"})
    print("create repo:", st)
else:
    print("repo exists:", st)
assert st in (200, 201), js

# --- git ---
env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
run = lambda c: subprocess.run(c, shell=True, cwd=BASE, env=env,
                               capture_output=True, text=True)
if not (BASE / ".git").exists():
    run("git init -b main")
    # credential store so the push has auth without a token on the command line
    cred = pathlib.Path(os.environ["HOME"]) / ".git-credentials"
    if not cred.exists():
        cred.write_text(f"https://x-access-token:{tok}@github.com\n")
        cred.chmod(0o600)
    run("git config --global credential.helper store")
    run(f"git remote add origin https://github.com/{OWNER}/{REPO}.git")

run("git add -A")
run('git -c user.email=banksy@agenttrac.local -c user.name=Banksy commit -m "Shift rota - 6 months, 3 staff"')
p = run("git push -u origin main --force")
print("push:", p.returncode, (p.stdout + p.stderr).strip()[-400:])

# --- pages ---
st, js = api("GET", f"/repos/{OWNER}/{REPO}/pages")
if st == 200:
    print("pages already on:", js.get("html_url"))
else:
    st, js = api("POST", f"/repos/{OWNER}/{REPO}/pages",
                 {"source": {"branch": "main", "path": "/"}})
    print("enable pages:", st, js.get("html_url") or js.get("message"))

URL = f"https://{OWNER}.github.io/{REPO}/"
print("URL:", URL)
for i in range(40):
    try:
        with urllib.request.urlopen(URL, timeout=15) as r:
            body = r.read().decode()
        if "Monday to Friday rota" in body:
            print(f"LIVE after {(i+1)*10}s: {len(body)} bytes")
            break
    except Exception:
        pass
    time.sleep(10)
else:
    print("NOT LIVE YET - re-check manually")

for path in ["rota.pdf", "rota.xlsx"]:
    try:
        req = urllib.request.Request(URL + path, method="HEAD")
        with urllib.request.urlopen(req, timeout=15) as r:
            print(path, r.status, r.headers.get("content-type"), r.headers.get("content-length"))
    except Exception as e:
        print(path, "ERR", e)
