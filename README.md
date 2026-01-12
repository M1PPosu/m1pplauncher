<div align="center">
  <img
    src="https://raw.githubusercontent.com/M1PPosu/m1pplauncher/refs/heads/main/icon.png"
    alt="M1PP Launcher"
    width="96"
    height="96"
  />

  <h1>M1PP Launcher</h1>

  <p>
    Windows launcher for connecting to <b>osu!stable</b> & <b>osu!lazer</b> private servers
    with optional mod tooling, an updater, logs, and
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
    <b style="color: #ff4d4d;">EARLY BETA:</b> Expect bugs. If something breaks,
    logs + a short repro go a long way.
  </p>
</div>

---

## TL;DR

- Stable routing: launches `osu!.exe -devserver <domain>`
- Lazer routing: launches `osu!.exe --api-url=<host> --website-url=<host>`
- Custom server routing: **osu!stable only** (no custom lazer routing)
- Beatmap Discord RPC requires telemetry (tosu). Stable uses `/json`, lazer uses `/json/v2`

---

## What this is (and what it isn’t)

M1PP Launcher exists to make connecting to **M1PPosu / M1Lazer** painless:

- One UI, two clients, correct routing every time
- Optional mods (built-in + custom `.mmod`)
- Built-in updater and logs for support

It’s a community launcher for community servers.  
It is **not affiliated with ppy** and it is **not for Bancho**.

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
    <td>Open M1PP Launcher → pick client → <b>LAUNCH</b></td>
    <td>That’s it</td>
  </tr>
</table>

---

## Routing model

### osu!stable

Stable routing is the classic devserver approach:

```txt
osu!.exe -devserver <domain>

Please note, to join a "custom" stable server all you have to do is enable to feature in settings, then input the domain e.g. sunrise.uk