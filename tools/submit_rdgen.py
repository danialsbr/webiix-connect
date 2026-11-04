#!/usr/bin/env python3
import pathlib
import re
import sys
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
ICON = ROOT / "branding" / "icon_ai.png"
# Use 256 square from res
ICON256 = ROOT / "res" / "icon.png"
LOGO = ROOT / "flutter" / "assets" / "logo_light.png"
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

from PIL import Image
import io

im = Image.open(ICON256).convert("RGBA").resize((256, 256))
buf = io.BytesIO()
im.save(buf, format="PNG")
icon_bytes = buf.getvalue()
logo_bytes = LOGO.read_bytes()

data = {
    "platform": "windows",
    "version": "1.5.0",
    "delayFix": "on",
    "exename": "WebiixConnect",
    "appname": "Webiix Connect",
    "direction": "both",
    "installation": "installationY",
    "settings": "settingsY",
    "androidappid": "",
    "serverIP": "188.121.103.222",
    "serverPort": "21116",
    "key": "tDmr3FJMFgJd2iWie3mEThnAPGOv17DdR1u7zrIm+cI=",
    "apiServer": "",
    "urlLink": "https://webiix.co/",
    "downloadLink": "https://webiix.co/",
    "compname": "Webiix",
    "passApproveMode": "password-click",
    "permanentPassword": "",
    "theme": "light",
    "themeDorO": "default",
    "permissionsDorO": "default",
    "permissionsType": "custom",
    "enableKeyboard": "on",
    "enableClipboard": "on",
    "enableFileTransfer": "on",
    "enableAudio": "on",
    "enableTCP": "on",
    "enableRemoteRestart": "on",
    "enableRecording": "on",
    "enableBlockingInput": "on",
    "enablePrinter": "on",
    "enableCamera": "on",
    "enableTerminal": "on",
    "removeWallpaper": "on",
    "removeNewVersionNotif": "on",
    "defaultManual": (
        "custom-rendezvous-server=188.121.103.222\n"
        "relay-server=188.121.103.222:21117\n"
        "key=tDmr3FJMFgJd2iWie3mEThnAPGOv17DdR1u7zrIm+cI=\n"
        "theme=light"
    ),
    "overrideManual": "",
}

files = {
    "iconfile": ("icon.png", icon_bytes, "image/png"),
    "logofile": ("logo.png", logo_bytes, "image/png"),
}

print("POST multipart to RDGen (light theme + webiix.co branding)...")
r = requests.post(
    "https://rdgen.crayoneater.org/generator",
    data=data,
    files=files,
    timeout=180,
)
print("status", r.status_code, "len", len(r.text))
(DIST / "rdgen-response.html").write_text(r.text, encoding="utf-8")

m = re.search(
    r"window\.location\.replace\('/check_for_file\?(.*?)'\);",
    r.text,
)
if not m:
    print("No build redirect found")
    print(r.text[:1500])
    sys.exit(1)

query = m.group(1)
print("query:", query)
(DIST / "rdgen-query.txt").write_text(query, encoding="utf-8")
params = dict(p.split("=", 1) for p in query.split("&"))
filename, uuid = params["filename"], params["uuid"]
base = "https://rdgen.crayoneater.org"
status_url = f"{base}/check_for_file?{query}"
print("status_url:", status_url)

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

out_h = pathlib.Path(r"H:\Webiix-Connect-Build\dist")
out_h.mkdir(parents=True, exist_ok=True)
out = DIST / f"{filename}_{uuid}"
out.mkdir(parents=True, exist_ok=True)
for name in (f"{filename}.exe", f"{filename}.msi"):
    url = f"{base}/download?filename={name}&uuid={uuid}"
    print("Downloading", url)
    for attempt in range(1, 6):
        try:
            d = session.get(url, timeout=600)
            if d.status_code == 200 and len(d.content) > 1000:
                (out / name).write_bytes(d.content)
                (out_h / name).write_bytes(d.content)
                print("Saved", out / name, "and H: copy", len(d.content), "bytes")
                break
            print("Skip/fail", name, d.status_code)
            break
        except requests.RequestException as e:
            print(f"download attempt {attempt} failed: {e}")
            time.sleep(15)
print("DONE", out)
