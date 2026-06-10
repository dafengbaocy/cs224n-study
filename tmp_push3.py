#!/usr/bin/env python3
import subprocess, os, base64, sys

os.chdir("/workspace/cs224n-study")

# Read token
env = {}
with open("/opt/data/.env") as f:
    for line in f:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k] = v.strip().strip('"').strip("'")

token = env.get("GITHUB_TOKEN", "")
if not token:
    print("No GITHUB_TOKEN found")
    sys.exit(1)

auth = base64.b64encode(f"x-access-token:{token}".encode()).decode()

# Add files
subprocess.run(["git", "add",
    "Labs/L01-word-vectors/co-occurrence-matrix.py",
    "Labs/L01-word-vectors/co-occurrence-matrix.ipynb"], check=False)

# Commit
r = subprocess.run(["git", "commit", "-m",
    "Update co-occurrence-matrix: fix CJK labels, add Chinese teaching notebook"],
    capture_output=True, text=True)
print(r.stdout)
print(r.stderr)

# Push
r = subprocess.run(["git", "-c",
    f"http.https://github.com/.extraheader=AUTHORIZATION: basic {auth}",
    "push", "origin", "main"],
    capture_output=True, text=True)
print(r.stdout)
print(r.stderr)
print(f"PUSH_EXIT={r.returncode}")
