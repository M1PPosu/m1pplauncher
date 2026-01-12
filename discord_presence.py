import os
import time
import threading
import queue
import json
import urllib.request
from dataclasses import dataclass
from typing import Optional, Tuple, Any, Dict, List

try:
    import psutil
except Exception:
    psutil = None

try:
    from pypresence import Presence
except Exception:
    Presence = None


@dataclass(frozen=True)
class PresencePayload:
    details: str
    state: str
    large_image: str
    large_text: str
    small_image: Optional[str] = None
    small_text: Optional[str] = None
    start_ts: Optional[int] = None
    end_ts: Optional[int] = None


class DiscordPresence:
    def __init__(self, client_id: str, logger):
        self._client_id = (client_id or "").strip()
        self._log = logger
        self._rpc = None
        self._stop = threading.Event()

        self._q: "queue.Queue[Optional[PresencePayload]]" = queue.Queue(maxsize=8)
        self._thread = threading.Thread(target=self._worker, name="DiscordPresenceRPC", daemon=True)
        self._thread.start()

        self._lock = threading.Lock()
        self._launch_until = 0.0

        self._tosu_url = (os.environ.get("M1PP_TOSU_URL", "").strip() or "http://127.0.0.1:24050/json")
        self._tosu_url_v2 = self._derive_v2_url(self._tosu_url)

        self._asset_launcher = os.environ.get("M1PP_RPC_ASSET_LAUNCHER", "m1ppweblogo").strip() or "m1ppweblogo"
        self._asset_stable = os.environ.get("M1PP_RPC_ASSET_STABLE", "m1ppweblogo").strip() or "m1ppweblogo"
        self._asset_lazer = os.environ.get("M1PP_RPC_ASSET_LAZER", "m1lazerlogo_1_").strip() or "m1lazerlogo_1_"
        self._asset_osu = os.environ.get("M1PP_RPC_ASSET_OSU", "osu__logo_2016_svg").strip() or "osu__logo_2016_svg"

        self._launcher_text = os.environ.get("M1PP_RPC_LAUNCHER_TEXT", "Mippo Launcher").strip() or "Mippo Launcher"

        self._enable_lazer_maps = (
            os.environ.get("M1PP_RPC_ENABLE_LAZER_MAPS", "1").strip().lower() not in ("0", "false", "no")
        )

        self._last_sent_key = ""
        self._supervisor = threading.Thread(target=self._supervisor_loop, name="DiscordPresenceSupervisor", daemon=True)
        self._supervisor.start()

    @staticmethod
    def create(client_id: str, logger) -> Optional["DiscordPresence"]:
        if not (client_id or "").strip():
            logger.info("DiscordPresence disabled (missing client_id).")
            return None
        if Presence is None:
            logger.warning("DiscordPresence disabled (missing dependency). Install: pip install pypresence")
            return None
        if psutil is None:
            logger.warning("DiscordPresence running without psutil; server detection may be limited.")
        return DiscordPresence(client_id, logger)

    def close(self):
        try:
            self._stop.set()
            self._enqueue(None)
        except Exception:
            pass

    def set_idle(self, server_label: str, large_image: str, large_text: str):
        self.set_launcher_idle()

    def set_launching(self, server_label: str, large_image: str, large_text: str):
        self.notify_launch_clicked()

    def set_playing(self, server_label: str, large_image: str, large_text: str):
        self.notify_launch_clicked()

    def set_launcher_idle(self):
        with self._lock:
            self._launch_until = 0.0

    def notify_launch_clicked(self, seconds: float = 45.0):
        with self._lock:
            self._launch_until = time.time() + max(5.0, float(seconds))

    def _enqueue(self, payload: Optional[PresencePayload]):
        try:
            while self._q.full():
                try:
                    self._q.get_nowait()
                except Exception:
                    break
            self._q.put_nowait(payload)
        except Exception:
            pass

    def _connect(self) -> bool:
        try:
            self._rpc = Presence(self._client_id)
            self._rpc.connect()
            self._log.info("DiscordPresence connected. client_id=%s", self._client_id)
            return True
        except Exception as e:
            self._rpc = None
            self._log.warning("DiscordPresence failed to connect: %s", e)
            return False

    def _update(self, p: PresencePayload):
        if self._rpc is None:
            return

        data = {
            "large_image": p.large_image,
            "large_text": p.large_text,
        }

        if p.details:
            data["details"] = p.details
        if p.state:
            data["state"] = p.state
        if p.small_image:
            data["small_image"] = p.small_image
        if p.small_text:
            data["small_text"] = p.small_text
        if p.start_ts is not None:
            data["start"] = int(p.start_ts)
        if p.end_ts is not None:
            data["end"] = int(p.end_ts)

        try:
            self._rpc.update(**data)
        except Exception as e:
            self._log.warning("DiscordPresence update failed: %s", e)
            try:
                self._rpc.close()
            except Exception:
                pass
            self._rpc = None

    def _worker(self):
        connected = False
        last_payload: Optional[PresencePayload] = None

        while not self._stop.is_set():
            if not connected or self._rpc is None:
                connected = self._connect()
                if connected and last_payload is not None:
                    self._update(last_payload)

            try:
                p = self._q.get(timeout=0.5)
            except Exception:
                p = None

            if self._stop.is_set():
                break

            if p is None:
                continue

            last_payload = p
            if connected and self._rpc is not None:
                self._update(p)

        try:
            if self._rpc is not None:
                try:
                    self._rpc.clear()
                except Exception:
                    pass
                try:
                    self._rpc.close()
                except Exception:
                    pass
        except Exception:
            pass

    def _supervisor_loop(self):
        self._push_if_changed(self._payload_launcher())

        while not self._stop.is_set():
            try:
                payload = self._compute_payload()
                if payload:
                    self._push_if_changed(payload)
            except Exception:
                pass
            time.sleep(1.0)

    def _push_if_changed(self, p: PresencePayload):
        key = (
            f"{p.details}|{p.state}|{p.large_image}|{p.large_text}|"
            f"{p.small_image or ''}|{p.small_text or ''}|{p.start_ts or ''}|{p.end_ts or ''}"
        )
        if key != self._last_sent_key:
            self._last_sent_key = key
            self._enqueue(p)

    def _compute_payload(self) -> PresencePayload:
        osu_ctx = self._detect_osu_context()

        if osu_ctx is None:
            with self._lock:
                launching = time.time() < self._launch_until

            if launching:
                return self._payload_launching()

            return self._payload_launcher()

        kind, host = osu_ctx
        server_display = self._display_server(kind, host)
        large_image, large_text = self._assets_for(kind, host)

        playing_info = None
        if kind == "lazer":
            if self._enable_lazer_maps:
                data = self._http_json(self._tosu_url_v2)
                playing_info = self._extract_playing_map_v2(data or {}) if data else None
        else:
            data = self._http_json(self._tosu_url)
            playing_info = self._extract_playing_map(data or {}) if data else None

        if playing_info:
            artist, title, diff, cur_ms, total_ms = playing_info
            map_line = f"{artist} - {title}".strip(" -")
            if diff:
                map_line = f"{map_line} [{diff}]"

            start_ts = None
            end_ts = None
            if total_ms > 0 and cur_ms >= 0:
                cur_s = max(0.0, cur_ms / 1000.0)
                rem_s = max(0.0, (total_ms - cur_ms) / 1000.0)
                start_ts = int(time.time() - cur_s)
                end_ts = int(time.time() + rem_s)

            return PresencePayload(
                details=map_line,
                state=f"Playing {server_display}",
                large_image=large_image,
                large_text=large_text,
                small_image=self._asset_osu,
                small_text="osu!",
                start_ts=start_ts,
                end_ts=end_ts,
            )

        return PresencePayload(
            details=f"Connected to {server_display}",
            state="",
            large_image=large_image,
            large_text=large_text,
            small_image=self._asset_osu,
            small_text="osu!",
        )

    def _payload_launcher(self) -> PresencePayload:
        return PresencePayload(
            details="Squatting in Launcher",
            state="",
            large_image=self._asset_launcher,
            large_text=self._launcher_text,
        )

    def _payload_launching(self) -> PresencePayload:
        return PresencePayload(
            details="Launching osu!",
            state="",
            large_image=self._asset_launcher,
            large_text=self._launcher_text,
        )

    def _strip_host(self, value: str) -> str:
        if not value:
            return ""
        v = value.strip()
        v = v.replace("https://", "", 1).replace("http://", "", 1)
        while v.endswith("/"):
            v = v[:-1]
        return v

    def _detect_osu_context(self) -> Optional[Tuple[str, Optional[str]]]:
        if psutil is None:
            return None

        cmds: List[List[str]] = []

        try:
            for p in psutil.process_iter(attrs=["name"]):
                name = (p.info.get("name") or "").lower()
                if name != "osu!.exe":
                    continue
                try:
                    cmd = p.cmdline()
                except Exception:
                    cmd = []
                if isinstance(cmd, list):
                    cmds.append(cmd)
        except Exception:
            pass

        if not cmds:
            return None

        for cmd in cmds:
            kind = self._classify_kind(cmd)
            host = self._extract_host(kind, cmd)
            if host:
                return (kind, host)

        kind = self._classify_kind(cmds[0])
        return (kind, None)

    def _classify_kind(self, cmd: List[str]) -> str:
        for a in cmd:
            if not isinstance(a, str):
                continue
            s = a.lower()
            if s.startswith("--api-url=") or s.startswith("--website-url=") or s.startswith("--lazer"):
                return "lazer"
        return "stable"

    def _extract_host(self, kind: str, cmd: List[str]) -> Optional[str]:
        if kind == "stable":
            for i, a in enumerate(cmd):
                if not isinstance(a, str):
                    continue
                s = a.lower()
                if s in ("-devserver", "--devserver"):
                    if i + 1 < len(cmd) and isinstance(cmd[i + 1], str):
                        return self._strip_host(cmd[i + 1])
                if s.startswith("--devserver="):
                    return self._strip_host(a.split("=", 1)[1])
            return None

        web = None
        api = None
        for a in cmd:
            if not isinstance(a, str):
                continue
            s = a.lower()
            if s.startswith("--website-url="):
                web = self._strip_host(a.split("=", 1)[1])
            elif s.startswith("--api-url="):
                api = self._strip_host(a.split("=", 1)[1])
        return web or api

    def _display_server(self, kind: str, host: Optional[str]) -> str:
        if not host:
            return "Unknown server"
        h = host.lower()

        if kind == "stable" and h.endswith("m1pposu.dev"):
            return "M1PP"
        if kind == "lazer" and h.endswith("m1pposu.dev"):
            return "M1Lazer"

        return host

    def _assets_for(self, kind: str, host: Optional[str]) -> Tuple[str, str]:
        if kind == "stable":
            if host and host.lower().endswith("m1pposu.dev"):
                return (self._asset_stable, "M1PP")
            return (self._asset_osu, "osu!")
        if kind == "lazer":
            if host and host.lower().endswith("m1pposu.dev"):
                return (self._asset_lazer, "M1Lazer")
            return (self._asset_osu, "osu!")
        return (self._asset_osu, "osu!")

    def _http_json(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "M1PPLauncher/1.0"})
            with urllib.request.urlopen(req, timeout=0.75) as resp:
                raw = resp.read()
            if not raw:
                return None
            return json.loads(raw.decode("utf-8", errors="replace"))
        except Exception:
            return None

    def _derive_v2_url(self, url: str) -> str:
        u = (url or "").strip()
        if not u:
            return "http://127.0.0.1:24050/json/v2"
        u = u.rstrip("/")
        if u.endswith("/json"):
            return u + "/v2"
        if u.endswith("/json/v2"):
            return u
        if "/json" in u:
            base = u.split("/json", 1)[0].rstrip("/")
            return base + "/json/v2"
        return u + "/json/v2"

    def _extract_playing_map(self, data: Dict[str, Any]) -> Optional[Tuple[str, str, str, int, int]]:
        if not isinstance(data, dict):
            return None

        state_val = None
        try:
            menu = data.get("menu") or {}
            state_val = menu.get("state")
            if state_val is None:
                state_val = data.get("status")
        except Exception:
            state_val = None

        artist = title = diff = ""
        cur_ms = total_ms = -1

        try:
            menu = data.get("menu") or {}
            bm = menu.get("bm") or menu.get("beatmap") or data.get("beatmap") or {}
            meta = bm.get("metadata") or bm.get("meta") or {}
            artist = (meta.get("artist") or bm.get("artist") or "").strip()
            title = (meta.get("title") or bm.get("title") or "").strip()
            diff = (
                (meta.get("difficulty") or meta.get("version") or bm.get("version") or bm.get("difficulty") or "")
                .strip()
            )

            t = bm.get("time") or menu.get("time") or data.get("time") or {}
            cur_ms = t.get("current") if isinstance(t, dict) else None
            total_ms = t.get("full") if isinstance(t, dict) else None

            if cur_ms is None:
                cur_ms = t.get("currentMs") if isinstance(t, dict) else None
            if total_ms is None:
                total_ms = t.get("total") if isinstance(t, dict) else None
            if total_ms is None:
                total_ms = t.get("fullMs") if isinstance(t, dict) else None

            play = data.get("play") or {}
            if (cur_ms is None or total_ms is None) and isinstance(play, dict):
                if cur_ms is None:
                    cur_ms = play.get("time")
                if total_ms is None:
                    total_ms = play.get("length")
        except Exception:
            pass

        if not title:
            return None

        try:
            cur_ms = int(cur_ms) if cur_ms is not None else -1
            total_ms = int(total_ms) if total_ms is not None else -1
        except Exception:
            cur_ms, total_ms = -1, -1

        playing = False
        try:
            if isinstance(state_val, (int, float, str)):
                try:
                    playing = int(state_val) == 2
                except Exception:
                    playing = False
        except Exception:
            playing = False

        if not playing:
            gp = data.get("gameplay") or {}
            combo = 0
            score = 0
            try:
                if isinstance(gp, dict):
                    combo = int(gp.get("combo") or 0)
                    score = int(gp.get("score") or 0)
            except Exception:
                combo = 0
                score = 0

            if total_ms > 0 and cur_ms >= 0 and (combo > 0 or score > 0 or cur_ms > 5000):
                playing = True

        if not playing:
            return None

        if total_ms <= 0 or cur_ms < 0:
            return (artist, title, diff, -1, -1)

        return (artist, title, diff, cur_ms, total_ms)

    def _extract_playing_map_v2(self, data: Dict[str, Any]) -> Optional[Tuple[str, str, str, int, int]]:
        if not isinstance(data, dict):
            return None

        bm = data.get("beatmap") or {}
        artist = (bm.get("artistUnicode") or bm.get("artist") or "").strip()
        title = (bm.get("titleUnicode") or bm.get("title") or "").strip()
        diff = (bm.get("version") or "").strip()

        if not title:
            return None

        t = bm.get("time") or {}
        try:
            cur_ms = int(t.get("live") or -1)
        except Exception:
            cur_ms = -1
        try:
            total_ms = int(t.get("lastObject") or -1)
        except Exception:
            total_ms = -1

        state = data.get("state") or {}
        s_name = str(state.get("name") or "").lower()
        try:
            s_num = int(state.get("number"))
        except Exception:
            s_num = None

        playing = (s_name == "playing") or (s_num == 2)

        if not playing:
            play = data.get("play") or {}
            combo = play.get("combo") or {}
            try:
                combo_cur = int(combo.get("current") or 0)
            except Exception:
                combo_cur = 0
            try:
                score = int(play.get("score") or 0)
            except Exception:
                score = 0

            if (combo_cur > 0) or (score > 0) or (cur_ms > 5000):
                playing = True

        if not playing:
            return None

        if total_ms <= 0 or cur_ms < 0:
            return (artist, title, diff, -1, -1)

        if total_ms < cur_ms:
            total_ms = -1

        return (artist, title, diff, cur_ms, total_ms)
