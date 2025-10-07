import random
import time
import json
import os
import threading
import webbrowser
from datetime import datetime
from typing import Optional
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.layout.dimension import Dimension
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
import textwrap

WORD_BANK = """
about above accept across act active activity actually add address age agree air all allow almost alone along already also always
and animal another answer any anyone anything appear apply area arrange arrive art as ask at attack attention audio available avoid away
baby back bad bag ball bank base be beat beautiful because become bed before begin behind believe benefit best better between big bill
bird bit black blood blue body book born both box boy break bring brother build building business but buy by call camera can capital car card care carry case catch
""".split()

RESULTS_FILE = os.path.expanduser("~/.terminal_monkeytype_results.json")
GITHUB_URL = "https://github.com/imaaquibali/"
console = Console()

class Session:
    def __init__(self, num_words: int, mode: str = "words", time_limit: int = 60):
        self.num_words = num_words
        self.target_words = random.choices(WORD_BANK, k=num_words)
        self.typed_chars: list[str] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.mistakes = 0
        self.correct_chars = 0
        self.total_typed = 0
        self.finished = False
        self.mode = mode
        self.time_limit = time_limit

    @property
    def target_text(self) -> str:
        return " ".join(self.target_words)

    def update_stats(self):
        elapsed = (time.time() - self.start_time) if self.start_time else 0.0001
        minutes = elapsed / 60.0
        wpm = (self.correct_chars / 5.0) / minutes if minutes > 0 else 0.0
        accuracy = (self.correct_chars / self.total_typed * 100.0) if self.total_typed > 0 else 100.0
        return wpm, accuracy, elapsed

def save_result(wpm, accuracy, num_words):
    rec = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "wpm": round(wpm, 1),
        "accuracy": round(accuracy, 1),
        "words": num_words
    }
    try:
        arr = []
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                arr = json.load(f)
        arr.append(rec)
        arr = arr[-50:]
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(arr, f, indent=2)
    except Exception:
        pass

def load_leaderboard():
    if not os.path.exists(RESULTS_FILE):
        return []
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def render_typing_fragments(session: Session):
    typed = "".join(session.typed_chars)
    target = session.target_text
    fragments = []

    app = get_app()
    width = app.output.get_size().columns
    height = app.output.get_size().rows - 6
    wrapped_lines = textwrap.wrap(target, width=width)
    cursor_pos = len(typed)
    current_line_idx = 0
    char_count = 0
    for idx, line in enumerate(wrapped_lines):
        if cursor_pos <= char_count + len(line):
            current_line_idx = idx
            break
        char_count += len(line)
    start_line = max(current_line_idx - height // 2, 0)
    visible_lines = wrapped_lines[start_line:start_line + height]
    rendered_lines = []
    global_idx = sum(len(l) for l in wrapped_lines[:start_line])
    for line in visible_lines:
        line_fragments = []
        for i, ch in enumerate(line):
            if global_idx < len(typed):
                if typed[global_idx] == ch:
                    line_fragments.append(("class:correct", ch))
                else:
                    line_fragments.append(("class:wrong", ch))
            elif global_idx == len(typed):
                line_fragments.append(("class:current", ch))
            else:
                line_fragments.append(("class:upcoming", ch))
            global_idx += 1
        line_fragments.append(("", "\n"))
        rendered_lines.extend(line_fragments)

    return rendered_lines

def render_status_line(session: Session):
    wpm, acc, elapsed = session.update_stats()
    if session.mode == "time":
        rem = max(0, session.time_limit - (elapsed if session.start_time else 0))
        return f"⏱ {elapsed:.1f}s (rem {int(rem)}s)   |   ⚡ {wpm:.1f} WPM   |   🎯 {acc:.1f}%   |   Mistakes: {session.mistakes}"
    else:
        return f"⏱ {elapsed:.1f}s   |   ⚡ {wpm:.1f} WPM   |   🎯 {acc:.1f}%   |   Mistakes: {session.mistakes}"

def start_timer_thread(app: Application, session: Session):
    def timer_loop():
        while not session.start_time and not session.finished:
            time.sleep(0.05)
        while not session.finished:
            elapsed = time.time() - session.start_time if session.start_time else 0
            if session.mode == "time" and elapsed >= session.time_limit:
                session.end_time = time.time()
                session.finished = True
                try:
                    app.exit()
                except Exception:
                    pass
                break
            time.sleep(0.06)
    t = threading.Thread(target=timer_loop, daemon=True)
    t.start()
    return t

def run_test():
    console.clear()
    console.print(Panel("[bold cyan]Terminal Monkeytype[/bold cyan]\n\nChoose mode:\n[1] Words (25 / 50 / 100)\n[2] Time  (15s / 30s / 60s / 120s)", title="Welcome", padding=(1,2)))
    pick = ""
    while pick not in ("1", "2"):
        pick = console.input("[green]Choice (1-words / 2-time): [/green]").strip()

    if pick == "1":
        console.print("\nPick word count: [1]25 [2]50 [3]100")
        p = ""
        while p not in ("1", "2", "3"):
            p = console.input("[green]Choice (1/2/3): [/green]").strip()
        num_words = 25 if p == "1" else 50 if p == "2" else 100
        mode = "words"
        time_limit = 0
    else:
        console.print("\nPick time: [1]15s [2]30s [3]60s [4]120s")
        p = ""
        while p not in ("1", "2", "3", "4"):
            p = console.input("[green]Choice (1/2/3/4): [/green]").strip()
        time_limit = 15 if p == "1" else 30 if p == "2" else 60 if p == "3" else 120
        num_words = time_limit * 3
        mode = "time"

    session = Session(num_words, mode=mode, time_limit=time_limit)
    kb = KeyBindings()

    @kb.add("escape")
    def _(event):
        session.finished = True
        event.app.exit()

    @kb.add("backspace")
    def _(event):
        if session.typed_chars:
            session.typed_chars.pop()
            typed = "".join(session.typed_chars)
            session.total_typed = len(typed)
            session.correct_chars = sum(1 for i, c in enumerate(typed) if i < len(session.target_text) and c == session.target_text[i])
            session.mistakes = session.total_typed - session.correct_chars
            event.app.invalidate()

    @kb.add(Keys.Any)
    def _(event):
        key = event.key_sequence[0].key
        if len(key) != 1:
            return
        if session.start_time is None:
            session.start_time = time.time()
        session.typed_chars.append(key)
        session.total_typed += 1
        idx = len(session.typed_chars) - 1
        if idx < len(session.target_text) and key == session.target_text[idx]:
            session.correct_chars += 1
        else:
            session.mistakes += 1
        if session.mode == "words":
            typed_str = "".join(session.typed_chars)
            completed_words = len([w for w in typed_str.strip().split(" ") if w != ""])
            if completed_words >= session.num_words:
                session.end_time = time.time()
                session.finished = True
                event.app.exit()
        event.app.invalidate()

    style = Style.from_dict({
        "correct": "bold green",
        "wrong": "bold red underline",
        "current": "bold reverse",
        "upcoming": "dim",
        "title": "bold cyan",
        "footer": "bold yellow"
    })

    layout = Layout(
        HSplit([
            VSplit([
                Window(content=FormattedTextControl([("class:title", "Terminal Monkeytype")]), align="center"),
                Window(width=20, content=FormattedTextControl([("class:footer", "")]), align="right")
            ], height=1),
            Window(height=6),
            Window(content=FormattedTextControl(lambda: render_typing_fragments(session)), height=Dimension(weight=1)),
            Window(height=1, content=FormattedTextControl(lambda: [("", render_status_line(session))])),
            Window(height=1, content=FormattedTextControl([("class:footer", "")]), align="center")
        ])
    )

    app = Application(layout=layout, key_bindings=kb, style=style, full_screen=True)
    start_timer_thread(app, session)

    try:
        app.run()
    except KeyboardInterrupt:
        session.finished = True

    if session.end_time is None:
        session.end_time = time.time()

    # Show results
    console.clear()
    wpm, acc, elapsed = session.update_stats()
    save_result(wpm, acc, session.num_words)
    summary = Table.grid(expand=True)
    summary.add_column(justify="center")
    summary.add_row(f"[bold magenta]Test Complete![/bold magenta]")
    summary.add_row(f"[bold]Mode:[/bold] {session.mode}   [bold]WPM:[/bold] {wpm:.1f}   [bold]Acc:[/bold] {acc:.1f}%   [bold]Time:[/bold] {int(elapsed)}s")
    panel = Panel(summary, title="RESULTS", border_style="bright_green", padding=(1,2))
    console.print(Align.center(panel))

    lb = load_leaderboard()[-5:][::-1]
    if lb:
        t = Table(title="Recent Results", expand=False)
        t.add_column("When")
        t.add_column("WPM")
        t.add_column("Acc")
        t.add_column("Words")
        for r in lb:
            t.add_row(r.get("timestamp","")[:19].replace("T"," "), str(r.get("wpm","")), str(r.get("accuracy","")), str(r.get("words","")))
        console.print(Align.center(t))

    # Menu / Retry / Github
    console.print("\n[r] Retry    [m] Menu    [q] Quit    [g] Github")
    while True:
        ch = console.input("\nChoice [r/m/q/g]: ").strip().lower()
        if ch == "r":
            run_test()
            return
        elif ch == "m":
            run_test()
            return
        elif ch == "q":
            console.print("Goodbye!")
            return
        elif ch == "g":
            webbrowser.open(GITHUB_URL)
            console.print("[green]Opened Github in browser![/green]")
        else:
            console.print("[dim]Invalid. Choose 'r', 'm', 'q', or 'g'.[/dim]")

def main():
    run_test()


if __name__ == "__main__":
    main()