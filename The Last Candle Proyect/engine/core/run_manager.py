"""
engine/core/run_manager.py
M7 — Run Manager

Gestiona el ciclo de vida completo de una run:
    - Generación y tracking de seed
    - Acumulación de estadísticas durante la run
    - Persistencia de historial en JSON
    - Pantalla de muerte/victoria con resumen completo
    - Flujo de nueva run
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import random
import json
import os
import time
from datetime import datetime

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule
from rich import box

from engine.ui.renderer import (
    console, show_message, get_player_input,
    pause, clear, C, ASCII_SKULL, ASCII_CANDLE,
)

SAVE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "save", "runs.json")
MAX_SAVED_RUNS = 10   # máximo de runs guardadas en el historial


# ------------------------------------------------------------------ #
#  Estructura de una run                                               #
# ------------------------------------------------------------------ #

@dataclass
class RunRecord:
    """Registro completo de una run — se persiste en JSON."""
    run_number:     int
    seed:           int
    player_class:   str
    player_name:    str

    # Progreso
    depth_reached:  int   = 0
    rooms_explored: int   = 0
    kills:          int   = 0
    gold_collected: int   = 0

    # Estado final
    cause_of_death: str   = "desconocido"
    victory:        bool  = False

    # Narrativa
    flags_set:      list  = field(default_factory=list)
    items_carried:  list  = field(default_factory=list)
    equipment_worn: dict  = field(default_factory=dict)

    # Meta
    timestamp:      str   = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    duration_secs:  int   = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> RunRecord:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ------------------------------------------------------------------ #
#  Persistencia                                                        #
# ------------------------------------------------------------------ #

def _load_history() -> list[RunRecord]:
    """Carga el historial de runs desde el archivo JSON."""
    try:
        if not os.path.exists(SAVE_PATH):
            return []
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [RunRecord.from_dict(r) for r in raw]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []   # archivo corrupto — empezar limpio


def _save_history(records: list[RunRecord]) -> None:
    """Guarda el historial. Mantiene solo los últimos MAX_SAVED_RUNS."""
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    trimmed = records[-MAX_SAVED_RUNS:]
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in trimmed], f, indent=2, ensure_ascii=False)


def _next_run_number() -> int:
    history = _load_history()
    return (history[-1].run_number + 1) if history else 1


# ------------------------------------------------------------------ #
#  Pantalla de muerte                                                  #
# ------------------------------------------------------------------ #

def _cause_label(cause: str) -> str:
    """Convierte el cause_of_death en texto narrativo."""
    if cause == "abandoned":
        return "Abandonaste."
    if cause == "sanity":
        return "La cordura te abandonó primero."
    if cause.startswith("killed_by:"):
        enemy = cause.replace("killed_by:", "").strip()
        return f"{enemy} acabó contigo."
    return cause


def show_run_summary(record: RunRecord, is_death: bool = True) -> None:
    """
    Pantalla de fin de run: muerte o victoria.
    Muestra estadísticas completas y extracto narrativo de la run.
    """
    clear()
    pause(0.4)

    if is_death:
        console.print()
        console.print(ASCII_SKULL)
        pause(0.3)
    else:
        console.print()
        console.print(ASCII_CANDLE)
        pause(0.3)

    # Título
    title_text = "HA MUERTO" if is_death else "HA SOBREVIVIDO"
    title_style = "bold red" if is_death else "bold green"
    console.print(f"\n  [{title_style}]{record.player_name.upper()} {title_text}[/{title_style}]\n")

    # Causa de muerte / victoria
    console.print(f"  [italic dim white]{_cause_label(record.cause_of_death)}[/italic dim white]\n")

    # Stats de run
    stats_table = Table(
        box=box.SIMPLE,
        border_style="dim white",
        show_header=False,
        padding=(0, 2),
    )
    stats_table.add_column("label", style="dim white",  width=22)
    stats_table.add_column("value", style="white",      width=14)
    stats_table.add_column("label2", style="dim white", width=22)
    stats_table.add_column("value2", style="white",     width=14)

    stats_table.add_row(
        "Clase",            record.player_class,
        "Seed",             str(record.seed),
    )
    stats_table.add_row(
        "Profundidad",      f"▼ {record.depth_reached}",
        "Salas exploradas", str(record.rooms_explored),
    )
    stats_table.add_row(
        "Criaturas caídas", str(record.kills),
        "Oro acumulado",    f"{record.gold_collected} monedas",
    )
    mins = record.duration_secs // 60
    secs = record.duration_secs % 60
    stats_table.add_row(
        "Duración",         f"{mins}m {secs}s",
        "Run nº",           f"#{record.run_number}",
    )

    console.print(Panel(stats_table, border_style="dim red" if is_death else "dim green",
                        box=box.SIMPLE_HEAVY))

    # Equipo que llevaba
    if record.equipment_worn:
        equip_text = Text()
        equip_text.append("\n  Equipo al morir:\n", style="dim white")
        slot_names = {"weapon": "Arma", "armor": "Armadura", "trinket": "Reliquia"}
        for slot, item_id in record.equipment_worn.items():
            from content.items.items_data import get_item
            item = get_item(item_id)
            name = item["name"] if item else item_id
            curse = " ⛧" if item and item.get("cursed") else ""
            equip_text.append(f"  {slot_names.get(slot, slot):12}", style="dim white")
            equip_text.append(f"{name}{curse}\n", style="cyan")
        console.print(equip_text)

    # Flags narrativos activados — los más interesantes
    _NARRATIVE_FLAGS = {
        "pacto_con_el_altar":      "Pactaste con el altar.",
        "mató_al_prisionero":      "Mataste al prisionero.",
        "liberó_al_prisionero":    "Liberaste al prisionero.",
        "pactó_con_el_susurro":    "Hiciste un trato con lo innombrable.",
        "conoce_la_verdad_del_dungeon": "Leíste el libro que no debía ser leído.",
        "deuda_con_lo_innombrable": "Tu deuda sigue pendiente.",
        "tiene_sangre_inocente":   "Llevas sangre inocente en las manos.",
        "el_reflejo_sabe":         "Tu reflejo sabe algo que tú no.",
        "completó_el_manuscrito":  "Completaste el manuscrito del escriba muerto.",
        "marcado_por_el_vacio":    "Estabas marcado desde el principio.",
        "abraza_el_dolor":         "Buscabas el dolor. Lo encontraste.",
    }

    narrative_flags = [
        msg for flag, msg in _NARRATIVE_FLAGS.items()
        if flag in record.flags_set
    ]

    if narrative_flags:
        console.print()
        console.print(Rule("[dim white]— Lo que quedará —[/dim white]", style="dim white"))
        for msg in narrative_flags:
            console.print(f"  [italic dim white]· {msg}[/italic dim white]")
        console.print()

    console.print()


def show_run_history() -> None:
    """Muestra el historial de runs anteriores."""
    history = _load_history()
    if not history:
        show_message("No hay runs anteriores.", style=C["muted"])
        return

    clear()
    console.print(Rule("[dim white]— Historial de Condenados —[/dim white]", style="dim white"))
    console.print()

    table = Table(
        box=box.SIMPLE_HEAVY,
        border_style="dim white",
        header_style="dim white",
        show_lines=False,
    )
    table.add_column("#",         style="dim white",  width=4,  justify="right")
    table.add_column("Clase",     style="cyan",       width=18)
    table.add_column("Fin",       style="white",      width=20)
    table.add_column("▼",         style="magenta",    width=4,  justify="center")
    table.add_column("Bajas",     style="red",        width=6,  justify="right")
    table.add_column("Oro",       style="yellow",     width=8,  justify="right")
    table.add_column("Fecha",     style="dim white",  width=18)

    for r in reversed(history[-8:]):
        end_str = "VICTORIA" if r.victory else _cause_label(r.cause_of_death)[:18]
        end_style = "bold green" if r.victory else "dim red"
        table.add_row(
            f"#{r.run_number}",
            r.player_name,
            f"[{end_style}]{end_str}[/{end_style}]",
            str(r.depth_reached),
            str(r.kills),
            str(r.gold_collected),
            r.timestamp,
        )

    console.print(table)
    console.print()


# ------------------------------------------------------------------ #
#  Run Manager principal                                               #
# ------------------------------------------------------------------ #

class RunManager:
    """
    Orquesta el ciclo de vida completo de una run.
    Instanciar uno por run; reutilizar para la siguiente.
    """

    def __init__(self):
        self.seed:        int           = random.randint(0, 999999)
        self.run_number:  int           = _next_run_number()
        self.start_time:  float         = time.time()
        self.record:      Optional[RunRecord] = None

    def start_run(self, player) -> RunRecord:
        """Inicializa el RunRecord al comienzo de la run."""
        self.start_time = time.time()
        self.record = RunRecord(
            run_number   = self.run_number,
            seed         = self.seed,
            player_class = player.player_class.value,
            player_name  = player.display_name,
        )
        return self.record

    def end_run(self, player, cause: str = "desconocido", victory: bool = False) -> RunRecord:
        """
        Cierra la run, captura el estado final del jugador y guarda en historial.
        cause: 'abandoned' | 'sanity' | 'killed_by:NombreEnemigo' | 'victory'
        """
        assert self.record is not None, "start_run() debe llamarse antes de end_run()"

        duration = int(time.time() - self.start_time)

        self.record.depth_reached   = player.depth
        self.record.rooms_explored  = player.rooms_explored
        self.record.kills           = player.kills
        self.record.gold_collected  = player.gold
        self.record.cause_of_death  = cause
        self.record.victory         = victory
        self.record.flags_set       = list(player.flags.keys())
        self.record.items_carried   = list(player.inventory)
        self.record.equipment_worn  = dict(player.equipment)
        self.record.duration_secs   = duration

        # Persistir
        history = _load_history()
        history.append(self.record)
        _save_history(history)

        return self.record

    def show_end_screen(self, is_death: bool = True) -> str:
        """
        Muestra la pantalla de fin de run y devuelve la acción del jugador:
        'restart' | 'history' | 'quit'
        """
        assert self.record is not None

        show_run_summary(self.record, is_death=is_death)

        console.print(Rule(style="dim white"))
        console.print()
        console.print("  [bold white]r[/bold white]  Nueva run  [dim white](nueva seed)[/dim white]")
        console.print("  [bold white]h[/bold white]  Ver historial de condenados")
        console.print("  [bold white]q[/bold white]  Salir")
        console.print()

        while True:
            raw = get_player_input("").strip().lower()
            if raw in ("r", "h", "q"):
                return raw
            show_message("r / h / q", style=C["danger"])
