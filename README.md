<div align="center">
  <img
    src="https://raw.githubusercontent.com/M1PPosu/m1pplauncher/refs/heads/main/icon.png"
    alt="M1PP Launcher"
    width="96"
    height="96"
  />

  <h1>M1PP Launcher</h1>

  <p>
    Windows launcher for <b>M1PP</b> / <b>M1Lazer</b> private osu! servers,
    with routing for <b>osu!stable</b> and <b>osu!lazer</b>, optional mod tooling,
    an updater, logs, and
    Discord Rich Presence.
  </p>

  <p>
    <a href="https://github.com/M1PPosu/m1pplauncher/releases/latest"><b>Download</b></a>
    ·
    <a href="https://discord.gg/RXQFFZx4ac"><b>Discord</b></a>
    ·
    <a href="#troubleshooting"><b>Troubleshooting</b></a>
    ·
    <a href="#building-from-source"><b>Build</b></a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPLv3" />
    <img
      src="https://img.shields.io/discord/1056311828344483840?label=discord&color=7289da"
      alt="Discord"
    />
    <img
      src="https://img.shields.io/github/downloads/M1PPosu/m1pplauncher/total"
      alt="GitHub Downloads"
    />
    <img
      src="https://img.shields.io/github/v/release/M1PPosu/m1pplauncher?color=dd00dd"
      alt="Latest Release"
    />
  </p>

  <p>
    <b style="color: #ff4d4d;">EARLY BETA:</b> Stability is still in progress.
    If something breaks, include logs and a short repro.
  </p>
</div>

---

## TL;DR

- Stable routing: launches `osu!.exe -devserver <domain>`
- Lazer routing: launches `osu!.exe --api-url=<host> --website-url=<host>`
- Custom server routing: **osu!stable only**
- Beatmap Discord RPC uses tosu telemetry: stable reads `/json`, lazer reads `/json/v2`

---

## What this is (and what it isn’t)

M1PP Launcher is the Windows desktop launcher for **M1PP / M1Lazer**.

- It routes both **osu!stable** and **osu!lazer** to the correct server endpoints
- It supports built-in mods and custom `.mmod` packages
- It includes an updater, logging, and Discord Rich Presence

It is **not affiliated with ppy**.  
It is **not intended for Bancho**.

---

## Quick start

<table>
  <tr>
    <td><b>1</b></td>
    <td>Download the latest release</td>
    <td><a href="https://github.com/M1PPosu/m1pplauncher/releases/latest">GitHub Releases</a></td>
  </tr>
  <tr>
    <td><b>2</b></td>
    <td>Run the installer <b>as Administrator</b></td>
    <td>Required for mklink + registry entries</td>
  </tr>
  <tr>
    <td><b>3</b></td>
    <td>Open M1PP Launcher → pick a client → <b>LAUNCH</b></td>
    <td>Routing is handled by the launcher</td>
  </tr>
</table>

---

## Routing model

### osu!stable

Stable routing uses the standard devserver launch argument:

```txt
osu!.exe -devserver <domain>
```

For a custom stable server, enable the **Custom Server** option in Settings and enter the target domain, for example `sunrise.uk`.

## Building From Source

The authoritative Windows build path is `build.bat` at the repo root.
It builds `m1ppupdater.exe` first, bundles it into the launcher, and writes `m1pplauncher.exe` to `dist\launcher\`.
