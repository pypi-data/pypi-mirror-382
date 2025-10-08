from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from platformdirs import user_data_path
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Select, Static

from ._scrambler import Scrambler

# Inspired by https://gist.github.com/yuanqing/ffa2244bd134f911d365
ASCII_DIGITS: dict[str, list[str]] = {
    "0": [" ███ ", "█   █", "█   █", "█   █", " ███ "],
    "1": ["  █  ", " ██  ", "  █  ", "  █  ", " ███ "],
    "2": [" ███ ", "█   █", "  ██ ", " █   ", "█████"],
    "3": [" ███ ", "█   █", "  ██ ", "█   █", " ███ "],
    "4": ["█   █", "█   █", "█████", "    █", "    █"],
    "5": ["█████", "█    ", "████ ", "    █", "████ "],
    "6": [" ███ ", "█    ", "████ ", "█   █", " ███ "],
    "7": ["█████", "   █ ", "  █  ", " █   ", "█    "],
    "8": [" ███ ", "█   █", " ███ ", "█   █", " ███ "],
    "9": [" ███ ", "█   █", " ████", "    █", " ███ "],
    ".": ["     ", "     ", "     ", "     ", "  ▄  "],
    ":": ["     ", "  ▄  ", "     ", "  ▄  ", "     "],
    " ": ["  ", "  ", "  ", "  ", "  "],
}

SESSIONS = [f"session{i}" for i in range(1, 16)]


def default_cstimer_blob() -> dict[str, object]:
    blob: dict[str, object] = {k: [] for k in SESSIONS}
    props = {
        "sessionData": json.dumps(
            {str(i): {"name": i, "opt": {}, "rank": i} for i in range(1, 16)}
        )
    }
    blob["properties"] = props
    return blob


@dataclass
class Solve:
    ms: int
    scramble: str
    when_epoch: int

    # TODO: penalty, DNF? currently always clean...
    def to_cstimer(self) -> list[object]:
        return [[0, self.ms], self.scramble, "", self.when_epoch]


def format_ms_as_mm_ss_mmm(ms: int) -> str:
    s_total = ms // 1000
    mmm = ms % 1000
    s = s_total % 60
    m = s_total // 60
    return f"{m:02d}:{s:02d}.{mmm:03d}"


def format_ns_as_mm_ss_mmmuuu(ns: int) -> str:
    total_us = ns // 1_000
    uuu = total_us % 1000
    total_ms = total_us // 1000
    mmm = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    m = total_s // 60
    return f"{m:02d}:{s:02d}.{mmm:03d}{uuu:03d}"


def ascii_render(text: str) -> str:
    rows = [""] * 5
    for ch in text:
        glyph = ASCII_DIGITS.get(ch, ASCII_DIGITS[" "])
        for i in range(5):
            rows[i] += glyph[i] + " "
    return "\n".join(rows)


def ao_n(times_ms: list[int], n: int) -> str:
    """Take the last n solves, drop the best and the worst (one each),
    and return the average formatted as mm:ss.mmm. If fewer than n
    solves exist, no average can be computed, so return "—"."""

    if len(times_ms) < n:
        return "—"
    window = sorted(times_ms[-n:])
    trimmed = window[1:-1]
    avg = sum(trimmed) // len(trimmed)
    return format_ms_as_mm_ss_mmm(avg)


class StatsPanel(Static):
    total_text = reactive("Total solves: 0", init=False)
    ao5_text = reactive("Ao5: —", init=False)
    ao12_text = reactive("Ao12: —", init=False)
    session_index = reactive(1, init=False)

    def compose(self) -> ComposeResult:
        select = Select[int](
            options=[(f"Session {i}", i) for i in range(1, 16)],
            value=self.session_index,
            id="session-select",
        )
        select.can_focus = False
        yield select
        yield Static(self.total_text, id="total")
        yield Static(self.ao5_text, id="ao5")
        yield Static(self.ao12_text, id="ao12")

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id != "session-select":
            return
        value = event.value
        # Guard NoSelection because we don't want to quit if a
        # user doesn't selection a session.
        if not isinstance(value, int):
            return
        self.session_index = value
        self.post_message(SessionChanged(self.session_index))

    def watch_total_text(self, val: str) -> None:
        if not self.is_mounted:
            return
        self.query_one("#total", Static).update(val)

    def watch_ao5_text(self, val: str) -> None:
        if not self.is_mounted:
            return
        self.query_one("#ao5", Static).update(val)

    def watch_ao12_text(self, val: str) -> None:
        if not self.is_mounted:
            return
        self.query_one("#ao12", Static).update(val)


class SessionChanged(Message):
    """Posted when the user selects a different session."""

    def __init__(self, session: int) -> None:
        self.session = session
        super().__init__()


class CubeTimer(App):
    # TODO: accessibility options (colors, contrast, font size), and audit
    # Gotta look into how to do this properly in TUI displays.
    CSS = """
    Screen {
        layout: horizontal;
    }
    #left {
        width: 28;
        padding: 1 2;
        border: tall $accent;
        height: 100%;
    }
    #main {
        layout: vertical;
        height: 100%;
        content-align: center top;
    }
    #scramble {
        padding: 1 2;
        height: auto;
        color: $accent;
        text-style: bold;
    }
    #timer {
        padding: 1 2;
        content-align: center middle;
        height: 1fr;
        text-style: bold;
        /* font-family/font not supported in Textual; terminals are monospaced */
    }
    #bottom {
        height: 3;
        padding: 0 1;
        color: $text-muted;
    }
    #total, #ao5, #ao12 {
        padding: 1 0 0 0;
    }
    """

    BINDINGS: ClassVar = [
        Binding("s", "new_scramble", "New scramble"),
        Binding("q", "stop_or_quit", "Stop/quit"),
        Binding("space", "start_stop", "Start/Stop", priority=True),
    ]

    # Plain attributes (not reactive) to satisfy typing
    running: bool = False
    start_ns: int | None = None
    current_ms: int = 0  # stored (cstimer compat)
    _tick = None  # repeating interval handle

    def __init__(self) -> None:
        super().__init__()
        self.rng = Scrambler.with_seed(time.time_ns())
        self.scramble = self.rng.generate()
        self.session = 1
        self.data_dir: Path = user_data_path(
            "cubetimer", "cubetimer", ensure_exists=True
        )
        self.file = self.data_dir / "cstimer.json"
        self.data = self._load_data()

    # ---------------- Storage -----------------------------
    def _load_data(self) -> dict[str, object]:
        if self.file.exists():
            try:
                return json.loads(self.file.read_text(encoding="utf-8"))
            except Exception:
                pass
        blob = default_cstimer_blob()
        self._save_data(blob)
        return blob

    def _save_data(self, blob: dict[str, object] | None = None) -> None:
        if blob is None:
            blob = self.data
        self.file.write_text(json.dumps(blob, ensure_ascii=False), encoding="utf-8")

    def _session_key(self) -> str:
        return f"session{self.session}"

    def _session_times_ms(self) -> list[int]:
        arr = self.data.get(self._session_key(), [])
        out: list[int] = []
        if isinstance(arr, list):
            for item in arr:
                try:
                    # item: [[pen, ms], scramble, "", epoch]
                    if (
                        isinstance(item, list)
                        and len(item) >= 1
                        and isinstance(item[0], list)
                        and len(item[0]) >= 2
                    ):
                        out.append(int(item[0][1]))
                except Exception:
                    continue
        return out

    # ------------------ User interface ------------------
    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="left"):
                self.stats = StatsPanel()
                yield self.stats
            with Vertical(id="main"):
                yield Static(self.scramble, id="scramble")
                self.timer_widget = Static(ascii_render("00:00.000000"), id="timer")
                yield self.timer_widget
                yield Static(
                    "Space: start/stop • S: new scramble • Q: stop (or quit if idle)",
                    id="bottom",
                )

    # TODO: doesn't work immediately on startup; need to tab out and then select
    # a session and it works. Bug in Textual? Or am I doing something wrong?
    def on_mount(self) -> None:
        self.set_focus(self.timer_widget)
        self._refresh_stats_panel()

    # ---------- Actions ----------
    def action_new_scramble(self) -> None:
        if self.running:
            return
        self.scramble = self.rng.generate()
        self.query_one("#scramble", Static).update(self.scramble)

    def action_start_stop(self) -> None:
        """Space toggles: start if idle; stop+record if running."""
        if self.running:
            self._stop_and_record()
        else:
            self._start()

    def action_stop_or_quit(self) -> None:
        if self.running:
            self._stop_and_record()
        else:
            self.exit()

    # ---------- Internal stuff ----------
    def _start(self) -> None:
        self.running = True
        self.start_ns = time.perf_counter_ns()
        self._paint()
        if self._tick is not None:
            self._tick.pause()
            self._tick = None
        self._tick = self.set_interval(0.005, self._on_tick, pause=False)

    def _on_tick(self) -> None:
        if not self.running or self.start_ns is None:
            return
        self._paint()

    def _paint(self) -> None:
        assert self.start_ns is not None
        elapsed_ns = time.perf_counter_ns() - self.start_ns
        self.current_ms = elapsed_ns // 1_000_000
        self.timer_widget.update(ascii_render(format_ns_as_mm_ss_mmmuuu(elapsed_ns)))

    def _stop_and_record(self) -> None:
        if self.start_ns is None:
            return
        final_ns = time.perf_counter_ns() - self.start_ns
        ms = final_ns // 1_000_000

        self.running = False
        self.start_ns = None
        if self._tick:
            self._tick.pause()
            self._tick = None

        solve = Solve(ms=ms, scramble=self.scramble, when_epoch=int(time.time()))
        sess_key = self._session_key()
        existing = self.data.get(sess_key)
        if isinstance(existing, list):
            existing.append(solve.to_cstimer())
        else:
            self.data[sess_key] = [solve.to_cstimer()]
        self._save_data()

        self._refresh_stats_panel()
        self.action_new_scramble()

        self.timer_widget.update(ascii_render(format_ns_as_mm_ss_mmmuuu(final_ns)))

    def _refresh_stats_panel(self) -> None:
        times = self._session_times_ms()
        self.stats.total_text = f"Total: {len(times)}"
        self.stats.ao5_text = f"Ao5:  {ao_n(times, 5)}"
        self.stats.ao12_text = f"Ao12: {ao_n(times, 12)}"
        sel = self.stats.query_one("#session-select", Select)
        if sel.value != self.session:
            sel.value = self.session

    # ----------------- Messages to the panel --------------------------
    def on_session_changed(self, message: SessionChanged) -> None:
        self.session = message.session
        self._refresh_stats_panel()


if __name__ == "__main__":
    CubeTimer().run()
