#!/usr/bin/env python3
"""Poll an already-started RDGen build and download artifacts."""
import pathlib
import re
import sys
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
query = (DIST / "rdgen-query.txt").read_text(encoding="utf-8").strip()
params = dict(p.split("=", 1) for p in query.split("&"))
filename = params["filename"]
uuid = params["uuid"]
base = "https://rdgen.crayoneater.org"
status_url = f"{base}/check_for_file?{query}"
print("Polling", status_url)

session = requests.Session()
elapsed = 0
while True:
    try:
        resp = session.get(status_url, timeout=90)
    except requests.RequestException as e:
        print(f"[{elapsed:04}s] poll error: {e}; retrying...", flush=True)
        time.sleep(30)
        elapsed += 30
        continue
    t = re.search(r"<title[^>]*>(.*?)</title>", resp.text, re.I)
    title = (t.group(1) if t else "").lower()
    stage = re.search(r'id="statusText"[^>]*>([^<]+)', resp.text)
    stage_txt = stage.group(1).strip() if stage else "?"
    print(f"[{elapsed:04}s] {title} | {stage_txt}", flush=True)
    if "generated" in title and "generating" not in title:
        if "Error: No file generated" in resp.text:
            print("Build failed")
            sys.exit(2)
        break
    time.sleep(30)
    elapsed += 30
    if elapsed > 9000:
        print("timeout")
        sys.exit(4)

out = DIST / f"{filename}_{uuid}"
out.mkdir(parents=True, exist_ok=True)
for name in (f"{filename}.exe", f"{filename}.msi"):
    url = f"{base}/download?filename={name}&uuid={uuid}"
    print("Downloading", url)
    for attempt in range(1, 6):
        try:
            d = session.get(url, timeout=600)
            if d.status_code == 200 and len(d.content) > 1000:
                path = out / name
                path.write_bytes(d.content)
                print("Saved", path, len(d.content), "bytes")
                break
            print("Skip/fail", name, d.status_code, len(d.content))
            break
        except requests.RequestException as e:
            print(f"download attempt {attempt} failed: {e}")
            time.sleep(15)
print("DONE", out)
