"""
tui.py — TUI completa con Textual.

Pantalla principal estilo Clue → selección de caso → detective narra el caso
→ tablero de investigación → backward / forward chaining interactivos.
"""

from __future__ import annotations

import asyncio
from importlib import import_module

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    Static,
)

from src.backward_chaining import BackwardWizard
from src.crime_case import CrimeCase
from src.forward_chaining import ForwardWizard
from src.predicate_logic import KnowledgeBase, Predicate, Term

# ─── Casos disponibles ────────────────────────────────────────────────────────

_CASE_MODULES = [
    "crimes.veneno_villa_espinas",
    "crimes.robo_expreso_sur",
    "crimes.sabotaje_pharmax",
    "crimes.herencia_hacienda_rosal",
    "crimes.red_puerto_sombras",
]

_STATUS_STYLE = {
    "culpable":   ("bold red",   "CULPABLE  "),
    "descartado": ("bold green", "DESCARTADO"),
    "sospechoso": ("yellow",     "SOSPECHOSO"),
    "?":          ("dim",        "   ???    "),
}

# Detective ASCII art — dos frames para animación
# Note: [[ and ]] are Rich's escaped square brackets
_DET_A = """
  ___________
 | DETECTIVE |
 |___________|
 (  o      o )
  \\  \u2500\u2500\u2500\u2500\u2500  /
  | [[NOTAS]] |
  |_________|"""

_DET_B = """
  ___________
 | DETECTIVE |
 |___________|
 (  \u2500      \u2500 )
  \\  \u2500\u2500\u2500\u2500\u2500  /
  | [[NOTAS]] |
  |_________|"""


def _load_case(module_name: str) -> CrimeCase:
    return import_module(module_name).CASE


def _parse_narrative_lines(narrative: str) -> list[str]:
    """Extrae líneas no vacías del docstring, omitiendo la primera (nombre de archivo)."""
    lines = narrative.strip().splitlines()
    # Skip first line if it looks like "filename.py — Title"
    if lines and ".py" in lines[0]:
        lines = lines[1:]
    return [ln.strip() for ln in lines if ln.strip()]


# ─── CSS ──────────────────────────────────────────────────────────────────────

CSS = """
Screen {
    background: #0d1117;
    color: #e6edf3;
}

/* ── Case Selector ─────────────────────────────── */

#selector-grid {
    layout: grid;
    grid-size: 2;
    grid-gutter: 1;
    padding: 1 2;
    height: auto;
}

.case-card {
    border: solid #21262d;
    padding: 1 2;
    height: 9;
    background: #161b22;
}

.case-card:hover {
    border: solid #58a6ff;
    background: #1c2128;
}

.case-card.--highlight {
    border: solid #f0c040;
    background: #1c2128;
}

.card-title {
    color: #f0c040;
    text-style: bold;
}

.card-meta {
    color: #6e7681;
    text-style: italic;
}

.card-desc {
    color: #c9d1d9;
}

/* ── Detective intro ────────────────────────────── */

#intro-container {
    layout: horizontal;
    height: 1fr;
}

#portrait-panel {
    width: 22;
    border: solid #30363d;
    padding: 0 1;
    background: #161b22;
    height: 100%;
}

#portrait-anim {
    color: #58a6ff;
    height: auto;
}

#det-label {
    color: #f0c040;
    text-style: bold;
    padding: 0 0 1 0;
}

#intro-right {
    layout: vertical;
    height: 100%;
}

#speech-area {
    height: 10;
    border: solid #30363d;
    padding: 1 2;
    background: #161b22;
}

#speech-phase {
    color: #f0c040;
    text-style: bold;
}

#speech-text {
    color: #e6edf3;
    padding: 1 0;
}

#speech-hint {
    color: #30363d;
    text-align: right;
}

#revealed-container {
    border: solid #21262d;
    background: #0a0e14;
    padding: 0 1;
    height: 1fr;
    overflow-y: auto;
}

#revealed-content {
    padding: 1;
}

/* ── Investigation board ───────────────────────── */

#board-container {
    layout: horizontal;
    height: 1fr;
}

#suspect-panel {
    width: 28;
    border: solid #30363d;
    padding: 0 1;
    background: #161b22;
}

#suspect-title {
    color: #f0c040;
    text-style: bold;
    padding: 0 1;
    border-bottom: solid #30363d;
}

.suspect-row {
    padding: 0 1;
    height: 2;
}

.suspect-status-culpable   { color: #f85149; text-style: bold; }
.suspect-status-descartado { color: #3fb950; }
.suspect-status-sospechoso { color: #d29922; }
.suspect-status-unknown    { color: #484f58; }

#kb-panel {
    border: solid #30363d;
    padding: 0 1;
    background: #0d1117;
}

#kb-title {
    color: #58a6ff;
    text-style: bold;
    padding: 0 1;
    border-bottom: solid #30363d;
}

#kb-content {
    color: #c9d1d9;
    padding: 1;
}

/* ── Backward / Forward screens ─────────────────── */

BackwardScreen, ForwardScreen {
    background: #0d1117 70%;
    align: center middle;
}

#modal-container {
    width: 90%;
    height: 90%;
    border: solid #58a6ff;
    background: #0d1117;
}

#modal-title {
    background: #1c2128;
    color: #58a6ff;
    text-style: bold;
    padding: 0 2;
    height: 3;
    content-align: left middle;
}

#modal-body {
    layout: horizontal;
    height: 1fr;
}

#modal-left {
    width: 40%;
    border-right: solid #21262d;
    padding: 0 1;
}

#modal-right {
    padding: 0 1;
    overflow-y: auto;
}

.section-title {
    color: #f0c040;
    text-style: bold;
    border-bottom: solid #21262d;
    padding: 0 1;
}

#tree-display {
    color: #c9d1d9;
    padding: 1;
}

#active-goal {
    color: #58a6ff;
    text-style: bold;
    padding: 1;
    border: dashed #58a6ff;
    margin: 1 0;
}

#log-display {
    color: #6e7681;
    padding: 1;
}

#rule-detail, #forward-rule-detail {
    color: #c9d1d9;
    padding: 1;
    border: dashed #30363d;
    margin: 1 0 0 0;
    height: auto;
    display: none;
}

ListView {
    background: #0d1117;
    border: solid #21262d;
}

ListItem {
    padding: 0 1;
    color: #c9d1d9;
}

ListItem:focus {
    background: #1c2128;
}

ListItem.--highlight {
    background: #1c2128;
    color: #f0c040;
}

/* ── Verdict ───────────────────────────────────── */

VerdictScreen {
    background: #0d1117 80%;
    align: center middle;
}

#verdict-box {
    width: 70;
    border: solid #f85149;
    background: #161b22;
    padding: 2 4;
}

#verdict-title {
    color: #f0c040;
    text-style: bold;
    text-align: center;
}

#verdict-culprit {
    color: #f85149;
    text-style: bold;
    text-align: center;
    padding: 1 0;
}

#verdict-chain {
    color: #c9d1d9;
    padding: 1 0;
}

/* ── Queries Screen ────────────────────────────── */

QueriesScreen {
    background: #0d1117 80%;
    align: center middle;
}

#queries-box {
    width: 80;
    border: solid #58a6ff;
    background: #161b22;
    padding: 2 4;
}

#queries-title {
    color: #58a6ff;
    text-style: bold;
    text-align: center;
    padding: 0 0 1 0;
    border-bottom: solid #21262d;
}

#queries-content {
    color: #c9d1d9;
    padding: 1 0;
}

/* ── Shared ────────────────────────────────────── */

.title-bar {
    background: #161b22;
    color: #f0c040;
    text-style: bold;
    height: 3;
    content-align: left middle;
    padding: 0 2;
    border-bottom: solid #21262d;
}

.separator {
    color: #21262d;
}

Button {
    background: #21262d;
    color: #c9d1d9;
    border: solid #30363d;
    min-width: 16;
}

Button:hover {
    background: #30363d;
    color: #f0c040;
    border: solid #58a6ff;
}

Button.-primary {
    background: #1f4068;
    color: #58a6ff;
    border: solid #58a6ff;
}
"""


# ─── Widgets ──────────────────────────────────────────────────────────────────


class AnimatedPortrait(Static):
    """Retrato ASCII que anima (alterna) entre dos frames."""

    def __init__(self, frames: tuple[str, str], **kwargs) -> None:
        self._frames = frames
        self._frame_idx = 0
        super().__init__(self._frames[0], **kwargs)

    def on_mount(self) -> None:
        self.set_interval(0.85, self._tick)

    def _tick(self) -> None:
        self._frame_idx ^= 1
        self.update(self._frames[self._frame_idx])


class SuspectRow(Static):
    """Fila de sospechoso en el tablero de investigación."""

    def __init__(self, key: str, status: str = "?", **kwargs) -> None:
        self._key = key
        self._status = status
        super().__init__("", **kwargs)
        self._refresh()

    def _refresh(self) -> None:
        style, label = _STATUS_STYLE.get(self._status, ("dim", "   ???    "))
        self.update(f"[bold]{self._key}[/]  [{style}]{label}[/]")

    def update_status(self, status: str) -> None:
        self._status = status
        self._refresh()


# ─── Screens ──────────────────────────────────────────────────────────────────


class CaseSelectorScreen(Screen):
    """Pantalla principal — elige el caso a investigar."""

    BINDINGS = [
        Binding("q", "quit", "Salir"),
        Binding("ctrl+c", "quit", "Salir", show=False),
        Binding("1", "select_case('0')", "Caso 1", show=False),
        Binding("2", "select_case('1')", "Caso 2", show=False),
        Binding("3", "select_case('2')", "Caso 3", show=False),
        Binding("4", "select_case('3')", "Caso 4", show=False),
        Binding("5", "select_case('4')", "Caso 5", show=False),
        Binding("enter", "open_selected", "Abrir", show=False),
    ]

    selected: reactive[int] = reactive(0)

    def __init__(self) -> None:
        super().__init__()
        self._cases = [_load_case(m) for m in _CASE_MODULES]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            "  [bold #f0c040]DETECTIVE LÓGICA[/] — [dim]Taller de IA · Uniandes[/]\n"
            "  [dim]Elige un caso para investigar  ·  teclas 1-5 o ↑↓ + Enter[/]",
            classes="title-bar",
        )
        with Container(id="selector-grid"):
            for i, case in enumerate(self._cases):
                quantifiers = self._quantifier_label(case)
                desc = case.description
                desc_display = (desc[:80] + "…") if len(desc) > 80 else desc
                yield Static(
                    f"[bold #f0c040]{i + 1}. {case.title}[/]\n"
                    f"[dim]{quantifiers}  {len(case.suspects)} sospechosos"
                    f"  ·  {len(case.queries)} consultas[/]\n"
                    f"[#c9d1d9]{desc_display}[/]",
                    id=f"card-{i}",
                    classes="case-card",
                )
        yield Footer()

    def _quantifier_label(self, case: CrimeCase) -> str:
        from src.predicate_logic import ExistsGoal, ForallGoal
        has_exists = any(isinstance(q.goal, ExistsGoal) for q in case.queries)
        has_forall = any(isinstance(q.goal, ForallGoal) for q in case.queries)
        parts = []
        if has_exists:
            parts.append("∃")
        if has_forall:
            parts.append("∀")
        return f"[{' '.join(parts)}]" if parts else ""

    def on_mount(self) -> None:
        self._highlight(0)

    def _highlight(self, idx: int) -> None:
        for i in range(len(self._cases)):
            card = self.query_one(f"#card-{i}")
            if i == idx:
                card.add_class("--highlight")
            else:
                card.remove_class("--highlight")
        self.selected = idx

    def on_key(self, event) -> None:
        if event.key == "up":
            self._highlight((self.selected - 1) % len(self._cases))
        elif event.key == "down":
            self._highlight((self.selected + 1) % len(self._cases))

    def action_select_case(self, idx_str: str) -> None:
        self._highlight(int(idx_str))
        self.action_open_selected()

    def action_open_selected(self) -> None:
        self.app.push_screen(CaseScreen(self._cases[self.selected]))

    def action_quit(self) -> None:
        self.app.exit()


# ─── Case Screen ──────────────────────────────────────────────────────────────


class CaseScreen(Screen):
    """
    Pantalla de investigación de un caso.

    Fase 'intro':  detective narra el caso y construye la KB line a línea.
    Fase 'board':  tablero de investigación con backward y forward chaining.
    """

    BINDINGS = [
        Binding("q", "go_back", "Volver"),
        Binding("enter", "advance", "Siguiente"),
        Binding("space", "advance", "Siguiente", show=False),
        Binding("k", "toggle_kb", "KB"),
        Binding("i", "open_backward", "Investigar"),
        Binding("f", "open_forward", "Hipótesis"),
        Binding("v", "show_verdict", "Veredicto"),
        Binding("t", "show_queries", "Consultas"),
    ]

    phase: reactive[str] = reactive("intro")

    def __init__(self, case: CrimeCase) -> None:
        super().__init__()
        self._case = case
        self._char_keys: list[str] = list(case.suspects)
        self._kb: KnowledgeBase = case.create_kb()
        self._fw = ForwardWizard(self._kb)
        # Start undecided — user discovers through forward/backward chaining
        self._statuses = {k: "?" for k in self._char_keys}
        self._all_facts = list(self._kb.facts)
        self._all_rules = list(self._kb.rules)

        # Intro state
        self._intro_items: list[tuple[str, str]] = self._build_intro_items()
        self._intro_idx: int = 0
        self._revealed_lines: list[str] = []

    # ── Intro item construction ───────────────────────────────────────────────

    def _build_intro_items(self) -> list[tuple[str, str]]:
        """Construye la lista de items para la introducción."""
        items: list[tuple[str, str]] = []
        # Narrative lines from module docstring
        if self._case.narrative:
            for line in _parse_narrative_lines(self._case.narrative):
                items.append(("narrative", line))
        # KB facts
        items.append(("heading", "Estos son los hechos que he registrado:"))
        for fact in self._all_facts:
            items.append(("fact", repr(fact.predicate)))
        # KB rules
        items.append(("heading", "Estas son mis reglas de deducción:"))
        for rule in self._all_rules:
            body = ", ".join(repr(b) for b in rule.body)
            items.append(("rule", f"{rule.head}  ←  {body}"))
        return items

    # ── Layout ────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            f"  [bold #f0c040]{self._case.title}[/]  "
            f"[dim]↵ avanzar  ·  K KB  ·  I investigar  ·  F hipótesis  ·  Q volver[/]",
            classes="title-bar",
        )
        # ── Intro phase ──
        with Container(id="intro-container"):
            with Vertical(id="portrait-panel"):
                yield Static("[bold #f0c040]DETECTIVE[/]", id="det-label")
                yield AnimatedPortrait((_DET_A, _DET_B), id="portrait-anim")
            with Vertical(id="intro-right"):
                with Container(id="speech-area"):
                    yield Static("", id="speech-phase")
                    yield Static("", id="speech-text")
                    yield Static(
                        "[dim]↵ ENTER → siguiente  ·  Q → volver[/]",
                        id="speech-hint",
                    )
                with ScrollableContainer(id="revealed-container"):
                    yield Static("", id="revealed-content")
        # ── Board phase (hidden) ──
        with Container(id="board-container"):
            with Vertical(id="suspect-panel"):
                yield Static("  SOSPECHOSOS", id="suspect-title")
                for key in self._char_keys:
                    yield SuspectRow(
                        key,
                        self._statuses.get(key, "?"),
                        id=f"suspect-{key}",
                        classes="suspect-row",
                    )
            with ScrollableContainer(id="kb-panel"):
                yield Static("  BASE DE CONOCIMIENTO", id="kb-title")
                yield Static(self._render_kb(), id="kb-content")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#board-container").display = False
        self._show_intro_item()

    # ── Intro phase ───────────────────────────────────────────────────────────

    def _phase_label(self, kind: str) -> str:
        if kind == "narrative":
            return "El detective lee el caso:"
        if kind == "heading":
            return ""
        if kind == "fact":
            return "Registrando hecho:"
        if kind == "rule":
            return "Regla de deducción:"
        return ""

    def _speech_style(self, kind: str, text: str) -> str:
        if kind == "narrative":
            return f'[italic #e6edf3]"{text}"[/]'
        if kind == "heading":
            return f"[bold #f0c040]{text}[/]"
        if kind == "fact":
            return f"[bold #3fb950]● {text}[/]"
        if kind == "rule":
            return f"[bold #58a6ff]▶ {text}[/]"
        return text

    def _revealed_style(self, kind: str, text: str) -> str:
        if kind == "narrative":
            return f"[dim #6e7681]  {text}[/]"
        if kind == "heading":
            return f"\n[bold #f0c040]── {text} ──[/]"
        if kind == "fact":
            return f"[dim #3fb950]  ● {text}[/]"
        if kind == "rule":
            return f"[dim #58a6ff]  ▶ {text}[/]"
        return f"[dim]  {text}[/]"

    def _show_intro_item(self) -> None:
        if self._intro_idx >= len(self._intro_items):
            self._switch_to_board()
            return

        kind, text = self._intro_items[self._intro_idx]
        phase_label = self._phase_label(kind)

        phase_widget = self.query_one("#speech-phase")
        phase_widget.update(phase_label)

        total = len(self._intro_items)
        counter = f"[dim]{self._intro_idx + 1}/{total}[/]"
        hint_widget = self.query_one("#speech-hint")
        hint_widget.update(
            f"{counter}  [dim]↵ ENTER → siguiente  ·  Q → volver[/]"
        )

        if kind == "heading":
            # Headings appear instantly, no typewriter
            self.query_one("#speech-text").update(self._speech_style(kind, text))
            self._add_to_revealed(kind, text)
        else:
            self._typewrite(text, kind)

    @work(exclusive=True)
    async def _typewrite(self, text: str, kind: str) -> None:
        target = self.query_one("#speech-text")
        delay = 0.018 if kind == "narrative" else 0.012
        revealed = ""
        for ch in text:
            revealed += ch
            if kind == "narrative":
                target.update(f'[italic #e6edf3]"{revealed}"[/]')
            elif kind == "fact":
                target.update(f"[bold #3fb950]● {revealed}[/]")
            elif kind == "rule":
                target.update(f"[bold #58a6ff]▶ {revealed}[/]")
            else:
                target.update(revealed)
            await asyncio.sleep(delay)
        # Finished — show final styled version
        target.update(self._speech_style(kind, text))

    def _add_to_revealed(self, kind: str, text: str) -> None:
        self._revealed_lines.append(self._revealed_style(kind, text))
        revealed_widget = self.query_one("#revealed-content")
        revealed_widget.update("\n".join(self._revealed_lines))
        # Scroll to bottom
        container = self.query_one("#revealed-container")
        container.scroll_end(animate=False)

    def action_advance(self) -> None:
        if self.phase == "board":
            return
        if self._intro_idx >= len(self._intro_items):
            self._switch_to_board()
            return

        kind, text = self._intro_items[self._intro_idx]
        # Add current item to revealed list (unless heading already added)
        if kind != "heading":
            self._add_to_revealed(kind, text)

        self._intro_idx += 1
        self._show_intro_item()

    # ── Board phase ───────────────────────────────────────────────────────────

    def _switch_to_board(self) -> None:
        self.phase = "board"
        self.query_one("#intro-container").display = False
        self.query_one("#board-container").display = True
        self._refresh_suspects()

    def _refresh_suspects(self) -> None:
        self._statuses = self._fw.suspect_statuses(self._char_keys)
        for key in self._char_keys:
            try:
                row = self.query_one(f"#suspect-{key}", SuspectRow)
                row.update_status(self._statuses.get(key, "?"))
            except Exception:
                pass

    def _render_kb(self) -> str:
        lines = ["[bold #58a6ff]HECHOS BASE[/]"]
        for fact in self._all_facts:
            lines.append(f"  [#3fb950]●[/] {fact.predicate}")
        lines.append("")
        lines.append("[bold #58a6ff]REGLAS[/]")
        for rule in self._all_rules:
            body = ", ".join(repr(b) for b in rule.body)
            lines.append(f"  [#f0c040]▶[/] [bold]{rule.head}[/]")
            lines.append(f"      [dim]:─ {body}[/]")
        return "\n".join(lines)

    def action_toggle_kb(self) -> None:
        kb_panel = self.query_one("#kb-panel")
        kb_panel.display = not kb_panel.display

    def action_open_backward(self) -> None:
        if self.phase != "board":
            self._switch_to_board()
        self.app.push_screen(
            BackwardScreen(self._kb, self._case, self._char_keys),
            callback=self._on_modal_close,
        )

    def action_open_forward(self) -> None:
        if self.phase != "board":
            self._switch_to_board()
        self.app.push_screen(
            ForwardScreen(self._fw, self._case, self._char_keys),
            callback=self._on_modal_close,
        )

    def action_show_verdict(self) -> None:
        if self.phase != "board":
            self._switch_to_board()
        self.app.push_screen(VerdictScreen(self._kb, self._case, self._fw, self._char_keys))

    def action_show_queries(self) -> None:
        if self.phase != "board":
            self._switch_to_board()
        self.app.push_screen(QueriesScreen(self._case, self._fw))

    def _on_modal_close(self, result=None) -> None:
        # Integrate backward chaining proven goals into forward wizard
        if isinstance(result, list):
            for goal in result:
                if goal not in self._fw.known:
                    self._fw.known.add(goal)
        self._refresh_suspects()

    def action_go_back(self) -> None:
        self.app.pop_screen()


# ─── Backward Chaining Screen ─────────────────────────────────────────────────


class BackwardScreen(ModalScreen):
    """Investigación interactiva de un sospechoso (backward chaining)."""

    BINDINGS = [
        Binding("escape", "dismiss", "Cerrar"),
        Binding("enter", "apply_choice", "Aplicar", show=False),
    ]

    _mode: reactive[str] = reactive("select_suspect")

    def __init__(
        self,
        kb: KnowledgeBase,
        case: CrimeCase,
        char_keys: list[str],
    ) -> None:
        super().__init__()
        self._kb = kb
        self._case = case
        self._char_keys = char_keys
        self._wizard: BackwardWizard | None = None
        self._proven_goals: list[Predicate] = []

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Static(
                "  INVESTIGAR SOSPECHOSO — Backward Chaining",
                id="modal-title",
            )
            with Horizontal(id="modal-body"):
                with ScrollableContainer(id="modal-left"):
                    yield Static("SOSPECHOSOS", classes="section-title")
                    yield ListView(
                        *[ListItem(Label(f"  {k}")) for k in self._char_keys],
                        id="suspect-list",
                    )
                    yield Static("", id="rule-title")
                    yield ListView(id="rule-list")
                    yield Static("", id="rule-detail")
                with ScrollableContainer(id="modal-right"):
                    yield Static("ÁRBOL DE PRUEBA", classes="section-title")
                    yield Static(
                        "[dim]← Elige un sospechoso para comenzar[/]",
                        id="active-goal",
                    )
                    yield Static("", id="tree-display")
                    yield Static("", id="log-display")

    def on_mount(self) -> None:
        self.query_one("#rule-title").display = False
        self.query_one("#rule-list").display = False
        self.query_one("#suspect-list").focus()

    @on(ListView.Selected, "#suspect-list")
    def on_suspect_selected(self, event: ListView.Selected) -> None:
        idx = event.list_view.index
        if idx is None:
            return
        char_key = self._char_keys[idx]
        goal = Predicate("culpable", (Term(char_key),))
        self._wizard = BackwardWizard(self._kb, goal)
        self._mode = "choose_rule"
        self._update_display()

    @on(ListView.Selected, "#rule-list")
    def on_rule_selected(self, event: ListView.Selected) -> None:
        if self._wizard is None:
            return
        idx = event.list_view.index
        if idx is None:
            return
        self._apply_choice(idx)

    @on(ListView.Highlighted, "#rule-list")
    def on_rule_highlighted(self, event: ListView.Highlighted) -> None:
        if self._wizard is None:
            return
        idx = event.list_view.index
        if idx is None:
            return
        detail_widget = self.query_one("#rule-detail")
        detail = self._wizard.option_detail(idx)
        if detail:
            detail_widget.update(detail)
            detail_widget.display = True
        else:
            detail_widget.display = False

    def action_dismiss(self) -> None:
        self.dismiss(self._proven_goals if self._proven_goals else None)

    def action_apply_choice(self) -> None:
        pass  # Handled via ListView.Selected

    def _apply_choice(self, idx: int) -> None:
        if self._wizard is None:
            return
        active = self._wizard.active_node
        if active is None:
            return
        if self._wizard.is_direct_fact(active.goal):
            if idx == 0:
                self._wizard.try_prove_as_fact()
            else:
                self._wizard.apply_rule(idx - 1)
        else:
            rules = self._wizard.matching_rules(active.goal)
            if not rules:
                self._wizard.mark_failed()
            else:
                self._wizard.apply_rule(idx)
        self._update_display()

    def _update_display(self) -> None:
        if self._wizard is None:
            return

        wizard = self._wizard
        tree_widget = self.query_one("#tree-display")
        active_widget = self.query_one("#active-goal")
        log_widget = self.query_one("#log-display")
        rule_list = self.query_one("#rule-list", ListView)
        rule_title = self.query_one("#rule-title")
        rule_detail = self.query_one("#rule-detail")

        tree_widget.update(wizard.tree_text())

        if wizard.log:
            log_widget.update("\n".join(f"[dim]{line}[/]" for line in wizard.log[-8:]))

        if wizard.is_complete:
            verdict = (
                "✅  [bold green]PROBADO[/]"
                if wizard.verdict
                else "❌  [bold red]NO PROBADO[/]"
            )
            active_widget.update(f"  Investigación completada\n  {verdict}")
            rule_title.display = False
            rule_list.display = False
            rule_detail.display = False
            if wizard.verdict:
                self._proven_goals.append(wizard.root.goal)
            self.query_one("#suspect-list").focus()
            return

        if wizard.active_node:
            active_widget.update(
                f"  Objetivo actual:\n  [bold #58a6ff]{wizard.active_node.goal}[/]"
            )

        options = wizard.current_options()
        rule_title.update("ELIGE CÓMO PROBAR ESTE OBJETIVO")
        rule_title.display = True
        rule_list.display = True
        rule_detail.display = False
        rule_list.focus()

        rule_list.clear()
        for opt in options:
            rule_list.append(ListItem(Label(f"  {opt}")))


# ─── Forward Chaining Screen ──────────────────────────────────────────────────


class ForwardScreen(ModalScreen):
    """Formulación de hipótesis (forward chaining) paso a paso."""

    BINDINGS = [
        Binding("escape", "dismiss", "Cerrar"),
        Binding("a", "apply_all", "Aplicar todas"),
    ]

    def __init__(
        self,
        wizard: ForwardWizard,
        case: CrimeCase,
        char_keys: list[str],
    ) -> None:
        super().__init__()
        self._case = case
        self._char_keys = char_keys
        self._wizard = wizard

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Static(
                "  FORMULAR HIPÓTESIS — Forward Chaining",
                id="modal-title",
            )
            with Horizontal(id="modal-body"):
                with ScrollableContainer(id="modal-left"):
                    yield Static("REGLAS APLICABLES", classes="section-title")
                    yield ListView(id="forward-rule-list")
                    yield Static("", id="forward-rule-detail")
                    yield Static(
                        "\n[dim]A → aplicar todas  ·  ESC → cerrar[/]",
                        id="forward-hint",
                    )
                with ScrollableContainer(id="modal-right"):
                    yield Static("HECHOS CONOCIDOS", classes="section-title")
                    yield Static("", id="forward-facts")
                    yield Static("", id="forward-log")

    def on_mount(self) -> None:
        self._update_display()
        self.query_one("#forward-rule-list").focus()

    @on(ListView.Selected, "#forward-rule-list")
    def on_rule_selected(self, event: ListView.Selected) -> None:
        idx = event.list_view.index
        if idx is None:
            return
        applicable = self._wizard.applicable()
        if idx < len(applicable):
            rule, fact = applicable[idx]
            self._wizard.apply(rule, fact)
            self._update_display()

    @on(ListView.Highlighted, "#forward-rule-list")
    def on_forward_rule_highlighted(self, event: ListView.Highlighted) -> None:
        idx = event.list_view.index
        if idx is None:
            return
        applicable = self._wizard.applicable()
        detail_widget = self.query_one("#forward-rule-detail")
        if idx < len(applicable):
            rule, fact = applicable[idx]
            detail = self._wizard.rule_detail(rule, fact)
            detail_widget.update(detail)
            detail_widget.display = True
        else:
            detail_widget.display = False

    def action_apply_all(self) -> None:
        while not self._wizard.is_complete():
            n = self._wizard.apply_all()
            if n == 0:
                break
        self._update_display()

    def _update_display(self) -> None:
        applicable = self._wizard.applicable()
        base, derived = self._wizard.known_by_source()
        statuses = self._wizard.suspect_statuses(self._char_keys)

        rule_list = self.query_one("#forward-rule-list", ListView)
        rule_detail = self.query_one("#forward-rule-detail")
        rule_list.clear()
        rule_detail.display = False
        if applicable:
            for rule, fact in applicable:
                label = self._wizard.rule_label(rule, fact)
                rule_list.append(ListItem(Label(f"  {label}")))
        else:
            rule_list.append(
                ListItem(Label("  [dim]✓ No hay más reglas que aplicar[/]"))
            )

        lines = [f"[bold #3fb950]HECHOS BASE ({len(base)}):[/]"]
        for f in base:
            lines.append(f"  [dim]●[/] {f}")
        lines.append("")
        lines.append(f"[bold #58a6ff]DERIVADOS ({len(derived)}):[/]")
        for f in derived:
            lines.append(f"  [#58a6ff]★[/] {f}")
        lines.append("")
        lines.append("[bold #f0c040]ESTADO SOSPECHOSOS:[/]")
        for key in self._char_keys:
            st = statuses.get(key, "?")
            style, label = _STATUS_STYLE.get(st, ("dim", "   ???    "))
            lines.append(f"  [{style}]{label}[/]  {key}")
        self.query_one("#forward-facts").update("\n".join(lines))

        if self._wizard.log:
            log_lines = ["[bold]PASOS:[/]"] + [
                f"  [dim]{line}[/]" for line in self._wizard.log[-10:]
            ]
            self.query_one("#forward-log").update("\n".join(log_lines))


# ─── Verdict Screen ───────────────────────────────────────────────────────────


class VerdictScreen(ModalScreen):
    """Pantalla de veredicto final."""

    BINDINGS = [
        Binding("escape", "dismiss", "Cerrar"),
        Binding("enter", "dismiss", "", show=False),
    ]

    def __init__(
        self,
        kb: KnowledgeBase,
        case: CrimeCase,
        fw: ForwardWizard,
        char_keys: list[str],
    ) -> None:
        super().__init__()
        self._kb = kb
        self._case = case
        self._fw = fw
        self._char_keys = char_keys

    def compose(self) -> ComposeResult:
        # Run full fixpoint to show definitive verdict
        full_fw = ForwardWizard(self._kb)
        while not full_fw.is_complete():
            if full_fw.apply_all() == 0:
                break
        statuses = full_fw.suspect_statuses(self._char_keys)
        culprits  = [k for k, s in statuses.items() if s == "culpable"]
        cleared   = [k for k, s in statuses.items() if s == "descartado"]
        suspects  = [k for k, s in statuses.items() if s == "sospechoso"]
        unknown   = [k for k, s in statuses.items() if s == "?"]

        lines = []
        if culprits:
            lines.append("[bold red]EL CULPABLE ES:[/]")
            for k in culprits:
                lines.append(f"  [bold red]▶  {k.upper()}[/]")
        lines.append("")
        if cleared:
            lines.append("[green]DESCARTADOS:[/]  " + ", ".join(cleared))
        if suspects:
            lines.append("[yellow]SOSPECHOSOS:[/]  " + ", ".join(suspects))
        if unknown:
            lines.append("[dim]SIN PRUEBAS:[/]   " + ", ".join(unknown))
        lines.append("")
        lines.append("[bold #58a6ff]PREGUNTAS DEL CASO:[/]")
        for q in self._case.queries:
            lines.append(f"  [dim]• {q.description}[/]")

        with Container(id="verdict-box"):
            yield Static(
                "  ══════════  VEREDICTO FINAL  ══════════",
                id="verdict-title",
            )
            yield Static(
                f"\n[bold #58a6ff]{_DET_A}[/]",
                id="verdict-chain",
            )
            yield Static("\n".join(lines))
            yield Static("\n  [dim]ENTER o ESC para cerrar[/]")


# ─── Queries Screen ───────────────────────────────────────────────────────────


class QueriesScreen(ModalScreen):
    """Muestra las preguntas del caso con resultados esperados."""

    BINDINGS = [
        Binding("escape", "dismiss", "Cerrar"),
        Binding("enter", "dismiss", "", show=False),
    ]

    def __init__(self, case: CrimeCase, fw: ForwardWizard) -> None:
        super().__init__()
        self._case = case
        self._fw = fw

    def compose(self) -> ComposeResult:
        from src.backward_chaining import backward_chain

        lines = ["[bold #f0c040]CONSULTAS DEL CASO[/]\n"]
        for i, q in enumerate(self._case.queries, 1):
            goal = q.goal
            r = backward_chain(self._fw.kb, goal)
            result_icon = "✓" if r.success else "✗"
            style = "#3fb950" if r.success else "#f85149"
            lines.append(f"  [{style}]{result_icon}[/] [{i}] {q.description}")
            lines.append("")

        with Container(id="queries-box"):
            yield Static("  CONSULTAS DE INVESTIGACIÓN", id="queries-title")
            yield Static("\n".join(lines), id="queries-content")
            yield Static("\n  [dim]ENTER o ESC para cerrar[/]")


# ─── Main App ─────────────────────────────────────────────────────────────────


class ClueTUI(App):
    """Aplicación principal."""

    TITLE = "Taller 3: Lógica Proposicional y de Predicados"
    SUB_TITLE = "Inteligencia Artificial — ISIS1611 · Uniandes"
    CSS = CSS
    SCREENS = {}
    CTRL_C_QUIT = True

    def on_mount(self) -> None:
        self.push_screen(CaseSelectorScreen())
