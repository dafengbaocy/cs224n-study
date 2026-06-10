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
files = [
    "Labs/L01-word-vectors/co-occurrence-matrix.py",
    "Labs/L01-word-vectors/co-occurrence-matrix.ipynb",
    "Labs/L01-word-vectors/outputs/co-occurrence-matrix-stdout.txt",
    "Labs/L01-word-vectors/outputs/co-occurrence-matrix-stderr.txt",
    "Labs/L01-word-vectors/outputs/co-occurrence-matrix-svd-2d.png",
    "Labs/L01-word-vectors/outputs/co-occurrence-matrix-svd-2d-window2.png",
    "Labs/L01-word-vectors/outputs/co-occurrence-matrix-summary.json",
    "Labs/L01-word-vectors/run-log.md",
]
subprocess.run(["git", "add"] + files, check=False)

# Commit
r = subprocess.run(["git", "commit", "-m",
    "Update co-occurrence-matrix: clean run with cat/dog/bank corpus, Chinese teaching notebook"],
    capture_output=True, text=True)
print("COMMIT:", r.stdout.strip())
if r.returncode != 0:
    print("COMMIT STDERR:", r.stderr.strip())

# Push
r = subprocess.run(["git", "-c",
    f"http.https://github.com/.extraheader=AUTHORIZATION: basic {auth}",
    "push", "origin", "main"],
    capture_output=True, text=True)
print("PUSH:", r.stdout.strip())
print("PUSH STDERR:", r.stderr.strip())
print(f"PUSH_EXIT={r.returncode}")
