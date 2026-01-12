<div align="center">
  <p align="center" style="color: red; font-weight: bold; font-size: 1.2em;">
    WARNING: This launcher is in early beta. Expect bugs and incomplete features!
  </p>

  <a href="https://github.com/M1PPosu/m1pplauncher">
    <img src="https://raw.githubusercontent.com/M1PPosu/m1pplauncher/refs/heads/main/icon.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">M1PP Launcher</h3>

  <p align="center">
    A Windows desktop launcher for routing <b>osu!stable</b> and <b>osu!lazer</b> to M1PP / M1Lazer community servers, with optional mod support and Discord Rich Presence.
    <br />
    <a href="https://github.com/M1PPosu/m1pplauncher/releases/latest"><strong>Download »</strong></a>
    <br />
    <br />

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Discord](https://img.shields.io/discord/1056311828344483840?label=discord&color=7289da)](https://discord.gg/RXQFFZx4ac)
[![Downloads](https://img.shields.io/github/downloads/M1PPosu/m1pplauncher/total)](https://github.com/M1PPosu/m1pplauncher/releases/latest)
[![Latest Release](https://img.shields.io/github/v/release/M1PPosu/m1pplauncher?color=dd00dd)](https://github.com/M1PPosu/m1pplauncher/releases/latest)

  </p>
</div>

---

## What this is
M1PP Launcher is a Windows launcher that helps players:

- Launch **osu!stable** with server routing via `-devserver`
- Launch **osu!lazer** with routing via `--api-url` and `--website-url`
- Optionally use supported mods (built-in and drop-in `.mmod` packages)
- Keep installs up-to-date via a bundled updater
- Provide Discord Rich Presence (including beatmap info when telemetry is available)

This project targets **community servers** (M1PP / M1Lazer). It is **not affiliated** with ppy or osu!.

---

## Quick start
1. Download the latest release from the link above.
2. Run the installer **as Administrator**.
3. Open **M1PP Launcher**.
4. Select **osu!stable** or **osu!lazer** and press **LAUNCH**.

---

## Features
- **Stable / Lazer toggle** from a single UI
- **Custom server routing (osu!stable only)** with validation checks
- **Mod system**
  - Built-in mods
  - Drop-in custom `.mmod` files
- **Self-updater** for launcher binary updates
- **Logging** for troubleshooting and support
- **Discord Rich Presence**
  - Server status derived from actual running process args
  - Beatmap + time remaining when telemetry is available

---

## How routing works

### osu!stable
Stable routing is done by launching:

- `osu!.exe -devserver <domain>`

The launcher sets the `-devserver` value based on your selection.

### osu!lazer
Lazer routing is done by launching:

- `osu!.exe --api-url=<host> --website-url=<host> --disable-sentry-logger`

Custom lazer routing is **not supported** at this time.

---

## Custom server routing (osu!stable only)
When enabled, the launcher uses the value from the custom server field as the `-devserver` target.

**Input rules**
- Enter **only** the domain/host, for example:
  - `m1pposu.dev`
  - `sunrize.uk`
- Do **not** type `-devserver` (the launcher adds it automatically)
- `http://` / `https://` is accepted but not required
- Invalid values are rejected (basic checks like whitespace and missing `.`)

---

## Mods

### Built-in mods
Built-in mods are shipped with the launcher.

### Custom mods (`.mmod`)
1. Open the mods folder from the UI, or navigate to `<install>\mods`
2. Drop `.mmod` files into the folder
3. Restart the launcher (recommended) and launch the game again

---

## Discord Rich Presence
The launcher provides Discord Rich Presence showing:
- Launcher state (idle / launching / connected)
- The server you are connected to (derived from the running process args)
- Beatmap + remaining time (when telemetry is available)

### Beatmap info requirements
Beatmap detection requires telemetry (e.g., **tosu**) to be running.

If beatmaps do not show:
- Ensure the tosu mod is enabled
- Verify telemetry endpoint is reachable:
  - `http://127.0.0.1:24050/json` (stable)
  - `http://127.0.0.1:24050/json/v2` (lazer)

---

## Safety note (important)
This launcher can inject mods and/or alter runtime behavior.

- Do **not** use injection tooling when connecting to official Bancho.
- You are responsible for how you use this launcher and any mods you enable.

---

## Where are logs?
Default logs are stored under:

- `%LOCALAPPDATA%\M1PPLauncher\logs\`

The updater may also write a standalone file:

- `%LOCALAPPDATA%\m1ppupdatelog-YYYYMMDD-HHMMSS.txt`

When reporting a bug, attach the most recent log file.

---

## Troubleshooting

### The launcher won’t open / crashes immediately
- Ensure you’re running the latest release
- Try running the installer/launcher as Administrator
- Attach the latest log from `%LOCALAPPDATA%\M1PPLauncher\logs\`

### Custom server isn’t applying (stable)
- Ensure **Use custom server** is enabled
- Ensure you entered **only** the host/domain (no `-devserver`)
- Confirm osu!stable is launched with `-devserver <domain>` (you can check via process cmdline tools)

### Beatmap isn’t showing in Discord
- Ensure telemetry (tosu) is enabled and running
- Check:
  - `http://127.0.0.1:24050/json` (stable)
  - `http://127.0.0.1:24050/json/v2` (lazer)

### Lazer launches but routes incorrectly
- Verify lazer is installed at:
  - `%LOCALAPPDATA%\osulazer\current\osu!.exe`
- Ensure ruleset installation succeeded (see logs)

---

## FAQ

### Is this launcher safe?
It’s designed for community servers, but it can inject mods, so you must use it responsibly. Avoid using injection tooling on Bancho.

### Does this work on macOS/Linux?
Not currently. Windows only.

### Can I use this launcher for my own private server?
Not officially. As of **January 7, 2026**, the project is not in a state where other servers should rely on it for production use. Contributions are welcome.

### Does lazer support custom server routing?
Not right now.

### Why does the installer need Administrator permissions?
The installer creates symlinks (`mklink`) and installs registry uninstall entries/shortcuts, which requires elevated permissions.

---

## Project structure (high level)
- `/installer` — installer wizard and install logic
- `/updater` — updater binary (and uninstall completion flow)
- `main.py` — launcher app entry
- `bootstrap.py` — routing/mod loading/injection utilities
- `discord_presence.py` — Discord Rich Presence integration
- `util.py` — shared config and resource helpers
- `m1pp_logger.py` — shared logging

---

## Building from source (Windows)

### Requirements
- Python (recommended: **3.12**)
- Visual Studio Build Tools (MSVC) if using `release.ps1` bootloader build
- Git

### Run locally
1. Create a venv
2. Install requirements
3. Run:

```bash
python main.py
