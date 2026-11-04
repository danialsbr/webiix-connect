# Webiix Connect

Free custom build of [RustDesk](https://github.com/rustdesk/rustdesk), rebranded for [Webiix](https://webiix.co/).

## Branding

| Item | Value |
|------|--------|
| App name | **Webiix Connect** |
| Website | https://webiix.co/ |
| License | Free |
| Icon | Infinity (Webiix logo) |

## Default relay (baked into the client)

| Setting | Value |
|---------|--------|
| ID Server | `188.121.103.222:21116` |
| Relay Server | `188.121.103.222:21117` |
| Key | `tDmr3FJMFgJd2iWie3mEThnAPGOv17DdR1u7zrIm+cI=` |

Import string (Network → Import server config):

```
9JSPJN2Ktlkc6dTdxIFZEdTM290RQFkboRVRtNTZpdVayQmSnZUTKZ0My1GR0JiOikXZrJCLiIiOikGchJCLicTMxEjM6IjMy4yMwEjLxITMugDOxIiOikXYsVmciwiI2ETMxIjOyIjMuMDMx4SMyEjL4gTMiojI0N3boJye
```

## What was changed in source

1. `libs/hbb_common/src/config.rs` — `APP_NAME`, `RENDEZVOUS_SERVERS`, `RS_PUB_KEY`, Webiix constants  
2. `src/webiix_defaults.rs` — applies name + default ID/Relay/Key at startup  
3. `Cargo.toml` / Windows / Android metadata — product name & copyright  
4. `res/` + `flutter/assets/` — Webiix infinity icons and logo  
5. English UI strings and About page → Webiix Connect  

Because `APP_NAME` is not `RustDesk`, the client is treated as a **custom client** (hides RustDesk pricing / update prompts).

## Build (Windows)

RustDesk needs a full native toolchain. Official guide:  
https://rustdesk.com/docs/en/dev/build/windows/

Summary:

1. Install Visual Studio (C++), Rust (`rustup`), LLVM, Flutter `3.24.5`, vcpkg  
2. Install vcpkg packages: `libvpx`, `libyuv`, `opus`, `aom` (`x64-windows-static`)  
3. From Git Bash in this repo:

```bash
export VCPKG_ROOT=/path/to/vcpkg
python3 branding/generate_assets.py   # refresh icons if needed
# Flutter desktop build (recommended):
# follow upstream flutter-build.yml / docs for your platform
cargo build --release --features flutter
```

Easiest path for a Windows `.exe`: push this repo to GitHub and run the existing Flutter build workflow (`.github/workflows/flutter-nightly.yml` / `flutter-tag.yml`), then download the artifact and rename the shortcut / installer display name if desired.

## After install

Config lives under `%APPDATA%\Webiix Connect\`. If an older RustDesk config interferes, remove that folder once, then relaunch so Webiix defaults apply cleanly.

## Regenerate icons

```bash
python branding/generate_assets.py
```

Uses `branding/icon_ai.png` and `branding/logo.png` as masters.
